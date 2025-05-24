#!/usr/bin/env python3
"""
Script to monitor consulate websites for changes and update information.
"""
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
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
        current_date = datetime.now().strftime("%B %d, %Y")
        
        for consulate_id, info in CONSULATES.items():
            logger.info(f"Checking {consulate_id}")
            if soup := get_website_content(info['url']):
                if changes := check_updates(soup, info):
                    try:
                        file = repo.get_contents(info['file'])
                        content = file.decoded_content.decode('utf-8')
                        updated_content = update_file_content(content, changes, current_date)
                        
                        if updated_content != content:
                            branch = f"update-{consulate_id}-{datetime.now().strftime('%Y%m%d')}"
                            
                            # Create branch using low-level API to avoid permission issues
                            main_ref = repo.get_git_ref("heads/main")
                            repo.create_git_ref(ref=f"refs/heads/{branch}", sha=main_ref.object.sha)
                            
                            # Update file in new branch
                            repo.update_file(
                                info['file'],
                                f"Update {consulate_id} consulate information",
                                updated_content,
                                file.sha,
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
