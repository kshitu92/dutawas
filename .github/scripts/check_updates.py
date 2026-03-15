#!/usr/bin/env python3
"""
Script to monitor consulate websites for changes and update information.
"""
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
from github import Github
import re
import logging
from config import CONSULATES

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_website_content(url: str):
    """Fetch website content"""
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; ConsulateUpdater/1.0; +https://dutawas.com)'}
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        logger.error(f"Failed to fetch {url}: {e}")
        return None

def check_updates(soup, consulate_info):
    """Extract updates from website"""
    changes = {}
    for field, config in consulate_info['selectors'].items():
        for element in soup.stripped_strings:
            if re.search(config['pattern'], element.strip(), re.IGNORECASE):
                changes[field] = element.strip()
                break
    return changes

def update_file_content(content, changes, current_date):
    """Update markdown file"""
    updated = content
    for field, new_value in changes.items():
        pattern = rf"\*{field.title()}:\*\s*.*?(?=\n\n|\n\*|$)"
        updated = re.sub(pattern, f"*{field.title()}:*  \n{new_value}", updated, flags=re.IGNORECASE | re.DOTALL)
    return re.sub(r"\*Page last updated:.*\*", f"*Page last updated: {current_date}*", updated)

def add_verification_timestamp(content, current_date):
    """Add or update 'Information last verified on:' timestamp in markdown file"""
    verification_line = f"*Information last verified on: {current_date} via automated monitoring*\n"
    
    # Check if verification line already exists
    if "**Information last verified on:**" in content:
        # Update existing verification line
        updated = re.sub(
            r"> \*\*Information last verified on:\*\*.*?\n",
            verification_line,
            content
        )
        return updated
    else:
        # Add verification line after the main heading (after first h1)
        lines = content.split('\n')
        insert_index = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                insert_index = i + 1
                break
        
        lines.insert(insert_index, "")
        lines.insert(insert_index + 1, verification_line.strip())
        return '\n'.join(lines)

def main():
    """Update consulate information"""
    try:
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN not set")
        
        repository = os.environ.get('GITHUB_REPOSITORY')
        if not repository:
            raise ValueError("GITHUB_REPOSITORY not set")
        
        g = Github(github_token)
        repo = g.get_repo(repository)
        tz_name = time.tzname[0] if time.daylight == 0 else time.tzname[1]
        current_date = datetime.now().strftime(f"%B %d, %Y at %I:%M %p {tz_name}")
        
        for consulate_id, info in CONSULATES.items():
            logger.info(f"Checking {consulate_id}")
            
            # Always update the verification timestamp
            try:
                file = repo.get_contents(info['file'])
                content = file.decoded_content.decode('utf-8')
                updated_content = add_verification_timestamp(content, current_date)
                
                # Update file in main branch with verification timestamp
                if updated_content != content:
                    repo.update_file(
                        path=info['file'],
                        message=f"Update verification timestamp for {consulate_id}",
                        content=updated_content,
                        sha=file.sha,
                        branch="main"
                    )
                    logger.info(f"Updated verification timestamp for {consulate_id}")
            except Exception as e:
                logger.error(f"Error updating verification timestamp for {consulate_id}: {e}")
            
            # Check for content updates
            if soup := get_website_content(info['url']):
                if changes := check_updates(soup, info):
                    try:
                        file = repo.get_contents(info['file'])
                        content = file.decoded_content.decode('utf-8')
                        updated_content = update_file_content(content, changes, current_date)
                        
                        if updated_content != content:
                            branch = f"update-{consulate_id}-{datetime.now().strftime('%Y%m%d')}"
                            
                            # Get the latest commit from main branch
                            main_branch = repo.get_branch("main")
                            main_sha = main_branch.commit.sha

                            # Create a new branch from main
                            repo.create_git_ref(ref=f"refs/heads/{branch}", sha=main_sha)

                            # Delete old branches if they exist
                            try:
                                repo.get_git_ref(f"heads/update-{consulate_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}").delete()
                            except:
                                pass
                            try:
                                repo.get_git_ref(f"heads/update-{consulate_id}-{datetime.now().strftime('%Y%m%d')}").delete()
                            except:
                                pass

                            # Update file in new branch
                            repo.update_file(
                                path=info['file'],
                                message=f"Update {consulate_id} consulate information",
                                content=updated_content,
                                sha=file.sha,
                                branch=branch
                            )
                            
                            # Create pull request
                            repo.create_pull(
                                title=f"Update {consulate_id} consulate information",
                                body=f"Updates found:\n" + "\n".join([f"- {k}: {v}" for k, v in changes.items()]),
                                head=branch,
                                base="main"
                            )
                            logger.info(f"Created PR for {consulate_id}")
                    except Exception as e:
                        logger.error(f"Error updating {consulate_id}: {e}")
                else:
                    logger.info(f"No updates for {consulate_id}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
