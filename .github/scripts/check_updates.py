#!/usr/bin/env python3
"""
Script to monitor consulate websites for changes in contact information and create pull requests for updates.
"""
import os
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from github import Github
import re
import logging
from config import CONSULATES

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_website_content(url: str):
    """Fetch website content with retries"""
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; ConsulateUpdater/1.0; +https://dutawas.com)'}
    for attempt in range(3):  # Try 3 times
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            if attempt == 2:  # Last attempt
                logger.error(f"Failed to fetch {url}: {e}")
                return None
            time.sleep(5)  # Wait before retry

def check_updates(soup, consulate_info):
    """Extract updates from website content"""
    changes = {}
    for field, config in consulate_info['selectors'].items():
        pattern = config['pattern']
        for element in soup.stripped_strings:
            text = element.strip()
            if re.search(pattern, text, re.IGNORECASE):
                changes[field] = text
                break
    return changes

def update_file_content(content, changes, current_date):
    """Update markdown file with new information"""
    updated = content
    for field, new_value in changes.items():
        pattern = rf"\*{field.title()}:\*\s*.*?(?=\n\n|\n\*|$)"
        replacement = f"*{field.title()}:*  \n{new_value}"
        updated = re.sub(pattern, replacement, updated, flags=re.IGNORECASE | re.DOTALL)
    
    # Update date
    updated = re.sub(
        r"\*Page last updated:.*\*",
        f"*Page last updated: {current_date}*",
        updated
    )
    return updated

def main():
    """Main function to check and update consulate information"""
    try:
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN not set")
        
        g = Github(github_token)
        repo = g.get_repo("kshitijlohani/dutawas")
        current_date = datetime.now().strftime("%B %d, %Y")
        
        for consulate_id, info in CONSULATES.items():
            logger.info(f"Checking {consulate_id}")
            
            soup = get_website_content(info['url'])
            if not soup:
                continue
            
            changes = check_updates(soup, info)
            if not changes:
                logger.info(f"No updates for {consulate_id}")
                continue
            
            try:
                file = repo.get_contents(info['file'])
                content = file.decoded_content.decode('utf-8')
                updated_content = update_file_content(content, changes, current_date)
                
                if updated_content != content:
                    branch = f"update-{consulate_id}-{datetime.now().strftime('%Y%m%d')}"
                    source = repo.get_branch("main")
                    repo.create_git_ref(f"refs/heads/{branch}", source.commit.sha)
                    
                    repo.update_file(
                        info['file'],
                        f"Update {consulate_id} consulate information",
                        updated_content,
                        file.sha,
                        branch=branch
                    )
                    
                    repo.create_pull(
                        title=f"Update {consulate_id} consulate information",
                        body=f"Updates found:\n" + "\n".join([f"- {k}: {v}" for k, v in changes.items()]),
                        head=branch,
                        base="main"
                    )
                    logger.info(f"Created PR for {consulate_id}")
            
            except Exception as e:
                logger.error(f"Error updating {consulate_id}: {e}")
                continue

    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
