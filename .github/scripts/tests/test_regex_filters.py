"""Validate that config.py regex patterns match content on live consulate pages."""

import os
import re
import sys
from functools import lru_cache

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from check_updates import check_updates, get_website_content
from config import CONSULATES


@lru_cache(maxsize=None)
def _fetch_soup(url: str):
    """Fetch and cache a page once per test session."""
    return get_website_content(url)


_params = [
    pytest.param(cid, field, cfg["pattern"], info["url"], id=f"{cid}::{field}")
    for cid, info in CONSULATES.items()
    for field, cfg in info["selectors"].items()
]


@pytest.mark.parametrize("consulate_id,field,pattern,url", _params)
def test_regex_pattern_is_valid(consulate_id, field, pattern, url):
    """Each pattern string in config.py must compile without error."""
    try:
        re.compile(pattern)
    except re.error as exc:
        pytest.fail(f"[{consulate_id}] Invalid regex for '{field}': {exc}")


@pytest.mark.parametrize("consulate_id,field,pattern,url", _params)
def test_regex_pattern_matches_live_html(consulate_id, field, pattern, url):
    """Each regex pattern must match at least one string on the live page."""
    soup = _fetch_soup(url)
    if soup is None:
        pytest.skip(f"[{consulate_id}] Could not reach {url}")

    changes = check_updates(soup, {"selectors": {field: {"pattern": pattern}}})

    assert field in changes, (
        f"[{consulate_id}] Pattern for '{field}' matched nothing on {url}.\n"
        f"Pattern: {pattern!r}"
    )
