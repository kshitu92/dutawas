import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from github import Github
import re
import logging
from typing import Dict, Optional
from config import CONSULATES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_website_content(url: str) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None

def check_updates(soup: BeautifulSoup, consulate_info: dict) -> Dict[str, str]:
    """Check for updates in the consulate information."""
    changes = {}
    
    for field, config in consulate_info['selectors'].items():
        pattern = config['pattern']
        found_text = soup.find(text=re.compile(pattern))
        
        if found_text:
            current_value = ' '.join(found_text.strip().split())
            with open(consulate_info['file'], 'r') as f:
                content = f.read()
                if current_value not in content:
                    changes[field] = current_value
    
    return changes

def update_file_content(content: str, changes: Dict[str, str], current_date: str) -> str:
    """Update the markdown file content with the changes."""
    for field, new_value in changes.items():
        pattern = f'\\*{field.title()}:\\*.*?(\\n\\n|$)'
        replacement = f'*{field.title()}:*\n{new_value}\n\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.IGNORECASE)
    
    # Update timestamp
    content = re.sub(
        r'\*Page last updated:.*\*',
        f'*Page last updated: {current_date}*',
        content
    )
    
    return content

def create_branch_and_pr(all_changes: Dict[str, Dict[str, str]]) -> Optional[str]:
    """Create a branch and PR with the changes."""
    if not all_changes:
        logger.info("No changes to create PR for")
        return None

    g = Github(os.environ['GITHUB_TOKEN'])
    repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
    
    # Create a new branch
    base = repo.get_branch("main")
    branch_name = f"auto-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    try:
        repo.create_git_ref(f"refs/heads/{branch_name}", base.commit.sha)
    except Exception as e:
        logger.error(f"Error creating branch: {e}")
        return None

    current_date = datetime.now().strftime('%B %d, %Y')
    
    # Update each file
    for consulate_name, changes in all_changes.items():
        file_path = CONSULATES[consulate_name]['file']
        try:
            file = repo.get_contents(file_path, ref=branch_name)
            content = file.decoded_content.decode()
            updated_content = update_file_content(content, changes, current_date)
            
            repo.update_file(
                file_path,
                f"Update {consulate_name} consulate information",
                updated_content,
                file.sha,
                branch=branch_name
            )
        except Exception as e:
            logger.error(f"Error updating {file_path}: {e}")
            continue

    # Create pull request
    try:
        pr = repo.create_pull(
            title=f"Auto-update: Consulate Information Changes {current_date}",
            body="Automated update of consulate information based on website changes.",
            head=branch_name,
            base="main"
        )
        logger.info(f"Created PR: {pr.html_url}")
        return pr.html_url
    except Exception as e:
        logger.error(f"Error creating PR: {e}")
        return None

def main():
    """Main function to check for updates across all consulates."""
    all_changes = {}
    
    for consulate_name, info in CONSULATES.items():
        logger.info(f"Checking {consulate_name} consulate...")
        soup = get_website_content(info['url'])
        if not soup:
            continue
        
        changes = check_updates(soup, info)
        if changes:
            logger.info(f"Found changes for {consulate_name}: {changes}")
            all_changes[consulate_name] = changes
    
    if all_changes:
        pr_url = create_branch_and_pr(all_changes)
        if pr_url:
            logger.info(f"Changes submitted in PR: {pr_url}")
    else:
        logger.info("No changes detected")

if __name__ == "__main__":
    main()
