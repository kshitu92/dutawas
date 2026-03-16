#!/usr/bin/env python3
"""
Script to monitor consulate websites for changes and update information.
"""
from __future__ import annotations

import logging
import os
import re
from datetime import datetime
from typing import Any

import requests
from bs4 import BeautifulSoup
from github import Github

from config import CONSULATES


USER_AGENT = "Mozilla/5.0 (compatible; ConsulateUpdater/1.0; +https://dutawas.com)"
REQUEST_TIMEOUT_SECONDS = 30
BASE_BRANCH = "main"
DATE_FORMAT = "%B %d, %Y"


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _require_env(name: str) -> str:
    """Read a required environment variable or raise a clear error."""
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"{name} not set")
    return value


def get_website_content(url: str):
    """Fetch website content"""
    headers = {'User-Agent': USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT_SECONDS)
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


def _delete_branch_if_exists(repo, branch_name: str) -> None:
    """Delete a branch if it already exists."""
    try:
        repo.get_git_ref(f"heads/{branch_name}").delete()
    except Exception:
        pass


def _create_update_branch(repo, consulate_id: str) -> str:
    """Create a fresh update branch from main and return its name."""
    branch_name = f"update-{consulate_id}-{datetime.now().strftime('%Y%m%d')}"
    main_sha = repo.get_branch(BASE_BRANCH).commit.sha

    _delete_branch_if_exists(repo, branch_name)
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_sha)
    return branch_name


def _open_pull_request(repo, consulate_id: str, changes: dict[str, str], branch_name: str) -> None:
    """Create a pull request for detected updates."""
    repo.create_pull(
        title=f"Update {consulate_id} consulate information",
        body="Updates found:\n" + "\n".join(f"- {k}: {v}" for k, v in changes.items()),
        head=branch_name,
        base=BASE_BRANCH
    )


def _process_consulate(repo, consulate_id: str, info: dict[str, Any], current_date: str) -> None:
    """Check one consulate and open a PR if file content changes."""
    logger.info(f"Checking {consulate_id}")

    soup = get_website_content(info['url'])
    if not soup:
        return

    changes = check_updates(soup, info)
    if not changes:
        logger.info(f"No updates for {consulate_id}")
        return

    file = repo.get_contents(info['file'])
    content = file.decoded_content.decode('utf-8')
    updated_content = update_file_content(content, changes, current_date)

    if updated_content == content:
        logger.info(f"No content changes for {consulate_id}")
        return

    branch_name = _create_update_branch(repo, consulate_id)
    repo.update_file(
        path=info['file'],
        message=f"Update {consulate_id} consulate information",
        content=updated_content,
        sha=file.sha,
        branch=branch_name
    )
    _open_pull_request(repo, consulate_id, changes, branch_name)
    logger.info(f"Created PR for {consulate_id}")


def main():
    """Update consulate information"""
    try:
        github_token = _require_env('GITHUB_TOKEN')
        repository = _require_env('GITHUB_REPOSITORY')

        repo = Github(github_token).get_repo(repository)
        current_date = datetime.now().strftime(DATE_FORMAT)

        for consulate_id, info in CONSULATES.items():
            try:
                _process_consulate(repo, consulate_id, info, current_date)
            except Exception as e:
                logger.error(f"Error updating {consulate_id}: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

if __name__ == "__main__":
    main()
