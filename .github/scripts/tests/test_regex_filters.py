"""
Validate that each regex pattern defined in config.py actually matches content
on the corresponding live consulate website.

The logic mirrors check_updates() in check_updates.py:
  - Fetch the page with BeautifulSoup
  - Iterate over soup.stripped_strings
  - Assert re.search(pattern, element, re.IGNORECASE) finds at least one match

Each consulate URL is fetched only once per test session (lru_cache).
Tests are skipped (not failed) when a URL is unreachable so CI stays green
even without external network access.
"""

import sys
import os
# Allow `from config import CONSULATES` regardless of where pytest is invoked from
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import re
import pytest
from functools import lru_cache

from check_updates import check_updates, get_website_content
from config import CONSULATES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _fetch_soup(url: str):
    """Fetch *url* once per test session using production fetch logic."""
    return get_website_content(url)


# ---------------------------------------------------------------------------
# Build parametrize input: one entry per (consulate, field)
# ---------------------------------------------------------------------------

_params = []
_ids = []
for _cid, _info in CONSULATES.items():
    for _field, _cfg in _info["selectors"].items():
        _params.append(
            pytest.param(
                _cid,
                _field,
                _cfg["pattern"],
                _info["url"],
                id=f"{_cid}::{_field}",
            )
        )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("consulate_id,field,pattern,url", _params)
def test_regex_pattern_matches_live_html(consulate_id, field, pattern, url):
    """Each regex pattern in config.py must match at least one string on the live page.

    Mirrors the check_updates() logic in check_updates.py exactly.
    """
    soup = _fetch_soup(url)
    if soup is None:
        pytest.skip(f"[{consulate_id}] Could not reach {url}")

    changes = check_updates(
        soup,
        {"selectors": {field: {"pattern": pattern}}},
    )

    assert field in changes, (
        f"\n[{consulate_id}] Pattern for '{field}' did not match any text on {url}.\n"
        f"Pattern : {pattern!r}\n"
        f"Tip     : Run the snippet below to inspect the page text:\n"
        f"  import requests, re\n"
        f"  from bs4 import BeautifulSoup\n"
        f"  soup = BeautifulSoup(requests.get('{url}', timeout=30).text, 'html.parser')\n"
        f"  print([s for s in soup.stripped_strings if re.search({pattern!r}, s, re.IGNORECASE)])"
    )


@pytest.mark.parametrize("consulate_id,field,pattern,url", _params)
def test_regex_pattern_is_valid(consulate_id, field, pattern, url):
    """Each pattern string must compile without error."""
    try:
        re.compile(pattern)
    except re.error as exc:
        pytest.fail(
            f"[{consulate_id}] Invalid regex for '{field}': {exc}\nPattern: {pattern!r}"
        )
