import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from github import Github
import re

def get_website_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def check_address_changes(soup):
    changes = {}
    # Look for address in the content
    address_text = soup.find(text=re.compile('Redmond Way'))
    if address_text:
        current_address = address_text.strip()
        # Compare with stored address
        with open('consulates/washington-state.md', 'r') as f:
            content = f.read()
            if current_address not in content:
                changes['address'] = current_address
    return changes

def create_branch_and_pr(changes):
    g = Github(os.environ['GITHUB_TOKEN'])
    repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])
    
    # Create a new branch
    base = repo.get_branch("main")
    branch_name = f"auto-update-{datetime.now().strftime('%Y%m%d')}"
    try:
        repo.create_git_ref(f"refs/heads/{branch_name}", base.commit.sha)
    except:
        print(f"Branch {branch_name} already exists")
        return

    # Update file
    file_path = 'consulates/washington-state.md'
    file = repo.get_contents(file_path, ref="main")
    content = file.decoded_content.decode()
    
    # Make updates
    if 'address' in changes:
        # Update address in content
        content = re.sub(
            r'\*Address:\*.*?United States of America',
            f'*Address:*\n{changes["address"]}\nUnited States of America',
            content,
            flags=re.DOTALL
        )
    
    # Update timestamp
    current_date = datetime.now().strftime('%B %d, %Y')
    content = re.sub(
        r'\*Page last updated:.*\*',
        f'*Page last updated: {current_date}*',
        content
    )

    # Commit file
    repo.update_file(
        file_path,
        f"Auto-update consulate information {current_date}",
        content,
        file.sha,
        branch=branch_name
    )

    # Create pull request
    pr = repo.create_pull(
        title=f"Auto-update: Consulate Information Changes {current_date}",
        body="Automated update of consulate information based on website changes.",
        head=branch_name,
        base="main"
    )
    
    print(f"Created PR: {pr.html_url}")

def main():
    url = "https://nepalconsulate.org"
    soup = get_website_content(url)
    if not soup:
        return
    
    changes = check_address_changes(soup)
    if changes:
        create_branch_and_pr(changes)
    else:
        print("No changes detected")

if __name__ == "__main__":
    main()
