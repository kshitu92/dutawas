"""Unit tests for check_updates.py."""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from bs4 import BeautifulSoup

# Allow importing check_updates.py when pytest is run from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import check_updates as sut


def test_require_env_returns_value(monkeypatch):
    monkeypatch.setenv("REQUIRED_VAR", "present")

    assert sut._require_env("REQUIRED_VAR") == "present"


def test_require_env_raises_when_missing(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)

    with pytest.raises(ValueError, match="MISSING_VAR not set"):
        sut._require_env("MISSING_VAR")


def test_get_website_content_success(monkeypatch):
    response = Mock()
    response.text = "<html><body><p>Hello</p></body></html>"
    response.raise_for_status = Mock()

    get_mock = Mock(return_value=response)
    monkeypatch.setattr(sut.requests, "get", get_mock)

    soup = sut.get_website_content("https://example.com")

    assert isinstance(soup, BeautifulSoup)
    assert "Hello" in list(soup.stripped_strings)
    get_mock.assert_called_once_with(
        "https://example.com",
        headers={"User-Agent": sut.USER_AGENT},
        timeout=sut.REQUEST_TIMEOUT_SECONDS,
    )


def test_get_website_content_failure_returns_none(monkeypatch):
    monkeypatch.setattr(sut.requests, "get", Mock(side_effect=RuntimeError("boom")))

    assert sut.get_website_content("https://example.com") is None


def test_check_updates_returns_first_match_per_field():
    html = """
    <div>
      <p>Address: 123 Main St Seattle WA 98001</p>
      <p>Call us: +1 (206) 555-1212</p>
      <p>Call us fallback: +1 (425) 555-0000</p>
    </div>
    """
    soup = BeautifulSoup(html, "html.parser")
    info = {
        "selectors": {
            "address": {"pattern": r"Seattle"},
            "phone": {"pattern": r"\(206\)\s*555-1212|\(425\)\s*555-0000"},
        }
    }

    changes = sut.check_updates(soup, info)

    assert changes == {
        "address": "Address: 123 Main St Seattle WA 98001",
        "phone": "Call us: +1 (206) 555-1212",
    }


def test_update_file_content_updates_matching_fields_and_page_date():
    original = (
        "## Contact\n\n"
        "*Address:*  \nOld Address\n\n"
        "*Phone:*  \nOld Phone\n\n"
        "*Page last updated: January 01, 2025*\n"
    )

    updated = sut.update_file_content(
        original,
        {"address": "New Address", "phone": "New Phone"},
        "March 16, 2026",
    )

    assert "*Address:*  \nNew Address" in updated
    assert "*Phone:*  \nNew Phone" in updated
    assert "*Page last updated: March 16, 2026*" in updated


def test_delete_branch_if_exists_deletes_ref():
    ref = Mock()
    repo = Mock()
    repo.get_git_ref.return_value = ref

    sut._delete_branch_if_exists(repo, "my-branch")

    repo.get_git_ref.assert_called_once_with("heads/my-branch")
    ref.delete.assert_called_once_with()


def test_create_update_branch_deletes_then_creates(monkeypatch):
    repo = Mock()
    repo.get_branch.return_value = SimpleNamespace(commit=SimpleNamespace(sha="abc123"))

    delete_mock = Mock()
    monkeypatch.setattr(sut, "_delete_branch_if_exists", delete_mock)

    class _FixedDateTime:
        @staticmethod
        def now():
            class _Now:
                @staticmethod
                def strftime(fmt):
                    return "20260316"

            return _Now()

    monkeypatch.setattr(sut, "datetime", _FixedDateTime)

    branch = sut._create_update_branch(repo, "new-york")

    assert branch == "update-new-york-20260316"
    delete_mock.assert_called_once_with(repo, "update-new-york-20260316")
    repo.create_git_ref.assert_called_once_with(
        ref="refs/heads/update-new-york-20260316",
        sha="abc123",
    )


def test_open_pull_request_builds_expected_payload():
    repo = Mock()

    sut._open_pull_request(
        repo,
        consulate_id="sydney",
        changes={"phone": "+61 2 1234 5678", "email": "info@example.com"},
        branch_name="update-sydney-20260316",
    )

    repo.create_pull.assert_called_once()
    kwargs = repo.create_pull.call_args.kwargs
    assert kwargs["title"] == "Update sydney consulate information"
    assert kwargs["head"] == "update-sydney-20260316"
    assert kwargs["base"] == sut.BASE_BRANCH
    assert "- phone: +61 2 1234 5678" in kwargs["body"]
    assert "- email: info@example.com" in kwargs["body"]


def test_process_consulate_stops_when_no_page(monkeypatch):
    repo = Mock()
    info = {"url": "https://example.com", "selectors": {}, "file": "consulates/x.md"}

    monkeypatch.setattr(sut, "get_website_content", Mock(return_value=None))

    sut._process_consulate(repo, "x", info, "March 16, 2026")

    repo.get_contents.assert_not_called()


def test_process_consulate_stops_when_no_changes(monkeypatch):
    repo = Mock()
    info = {"url": "https://example.com", "selectors": {}, "file": "consulates/x.md"}

    monkeypatch.setattr(sut, "get_website_content", Mock(return_value=object()))
    monkeypatch.setattr(sut, "check_updates", Mock(return_value={}))

    sut._process_consulate(repo, "x", info, "March 16, 2026")

    repo.get_contents.assert_not_called()


def test_process_consulate_full_flow(monkeypatch):
    file_obj = SimpleNamespace(
        decoded_content=b"*Address:*  \nOld\n\n*Page last updated: Jan 01, 2025*",
        sha="file-sha",
    )
    repo = Mock()
    repo.get_contents.return_value = file_obj

    info = {
        "url": "https://example.com",
        "file": "consulates/united-states/new-york.md",
        "selectors": {"address": {"pattern": "Address"}},
    }

    monkeypatch.setattr(sut, "get_website_content", Mock(return_value=object()))
    monkeypatch.setattr(sut, "check_updates", Mock(return_value={"address": "New Address"}))
    monkeypatch.setattr(sut, "update_file_content", Mock(return_value="new markdown"))
    monkeypatch.setattr(sut, "_create_update_branch", Mock(return_value="update-branch"))
    open_pr_mock = Mock()
    monkeypatch.setattr(sut, "_open_pull_request", open_pr_mock)

    sut._process_consulate(repo, "new-york", info, "March 16, 2026")

    repo.update_file.assert_called_once_with(
        path="consulates/united-states/new-york.md",
        message="Update new-york consulate information",
        content="new markdown",
        sha="file-sha",
        branch="update-branch",
    )
    open_pr_mock.assert_called_once_with(
        repo,
        "new-york",
        {"address": "New Address"},
        "update-branch",
    )


def test_process_consulate_skips_when_content_unchanged(monkeypatch):
    content = "same markdown"
    file_obj = SimpleNamespace(decoded_content=content.encode("utf-8"), sha="file-sha")
    repo = Mock()
    repo.get_contents.return_value = file_obj

    info = {
        "url": "https://example.com",
        "file": "consulates/united-states/new-york.md",
        "selectors": {"address": {"pattern": "Address"}},
    }

    monkeypatch.setattr(sut, "get_website_content", Mock(return_value=object()))
    monkeypatch.setattr(sut, "check_updates", Mock(return_value={"address": "Still same"}))
    monkeypatch.setattr(sut, "update_file_content", Mock(return_value=content))

    create_branch_mock = Mock()
    monkeypatch.setattr(sut, "_create_update_branch", create_branch_mock)

    sut._process_consulate(repo, "new-york", info, "March 16, 2026")

    create_branch_mock.assert_not_called()
    repo.update_file.assert_not_called()


def test_main_processes_all_consulates(monkeypatch):
    fake_repo = Mock()
    fake_client = Mock()
    fake_client.get_repo.return_value = fake_repo

    monkeypatch.setenv("GITHUB_TOKEN", "token")
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setattr(sut, "Github", Mock(return_value=fake_client))
    monkeypatch.setattr(sut, "CONSULATES", {"a": {"url": "u", "file": "f", "selectors": {}}, "b": {"url": "u", "file": "f", "selectors": {}}})

    process_mock = Mock()
    monkeypatch.setattr(sut, "_process_consulate", process_mock)

    sut.main()

    assert process_mock.call_count == 2
