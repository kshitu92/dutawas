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

def delete_old_branch(repo, branch_prefix, consulate_id):
    """Delete old update branches for a consulate"""
    try:
        # Fix: Use the correct method signature for get_git_refs
        refs = repo.get_git_matching_refs(f"heads/{branch_prefix}{consulate_id}-")
        for ref in refs:
            logger.info(f"Deleting old branch: {ref.ref}")
            ref.delete()
    except Exception as e:
        logger.warning(f"Failed to delete old branches: {e}")

def create_commit_and_push(repo, file, message, content, branch):
    """Create a commit and push changes"""
    try:
        # Get the main branch's latest commit
        main_ref = repo.get_git_ref("heads/main")
        base_tree = repo.get_git_tree(main_ref.object.sha)
        
        # Create blob for the new file content
        blob = repo.create_git_blob(content, "utf-8")
        element = {"path": file.path, "mode": "100644", "type": "blob", "sha": blob.sha}
        
        # Create tree with the new blob
        tree = repo.create_git_tree([element], base_tree)
        
        # Create commit
        parent = repo.get_git_commit(main_ref.object.sha)
        commit = repo.create_git_commit(message, tree, [parent])
        
        # Create or update branch reference
        try:
            ref = repo.create_git_ref(f"refs/heads/{branch}", commit.sha)
        except:
            ref = repo.get_git_ref(f"heads/{branch}")
            ref.edit(commit.sha, force=True)
            
        return True
    except Exception as e:
        logger.error(f"Error in create_commit_and_push: {e}")
        return False

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
                            # Include timestamp in branch name
                            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                            branch_prefix = "update-"
                            branch = f"{branch_prefix}{consulate_id}-{timestamp}"
                            
                            # Delete any existing update branches
                            delete_old_branch(repo, branch_prefix, consulate_id)
                            
                            # Create commit and push changes
                            if create_commit_and_push(repo, file, f"Update {consulate_id} consulate information", updated_content, branch):
                                try:
                                    # Try to create pull request
                                    repo.create_pull(
                                        title=f"Update {consulate_id} consulate information",
                                        body=f"Updates found:\n" + "\n".join([f"- {k}: {v}" for k, v in changes.items()]),
                                        head=branch,
                                        base="main"
                                    )
                                    logger.info(f"Created PR for {consulate_id}")
                                except Exception as e:
                                    logger.warning(f"Could not create PR, but changes are pushed to branch {branch}: {e}")
                                    logger.info("Please create the pull request manually from the branch.")
                    except Exception as e:
                        logger.error(f"Error updating {consulate_id}: {e}")
                else:
                    logger.info(f"No updates for {consulate_id}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
