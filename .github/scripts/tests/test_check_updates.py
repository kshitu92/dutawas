"""Unit tests for check_updates.py."""

from __future__ import annotations

import os
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest
from bs4 import BeautifulSoup

# Allow importing check_updates.py when pytest is run from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import check_updates as sut

# ---------------------------------------------------------------------------
# Shared test constants
# ---------------------------------------------------------------------------
EXAMPLE_URL = "https://example.com"
EXAMPLE_HTML = "<html><body><p>Hello</p></body></html>"
CURRENT_DATE = "March 16, 2026"
BRANCH_DATE_STAMP = "20260316"
FILE_SHA = "file-sha"
MAIN_SHA = "abc123"
CONSULATE_FILE = "consulates/united-states/new-york.md"
CONSULATE_ID_NY = "new-york"
CONSULATE_ID_SYDNEY = "sydney"
BRANCH_NAME_NY = f"update-{CONSULATE_ID_NY}-{BRANCH_DATE_STAMP}"
BRANCH_NAME_SYDNEY = f"update-{CONSULATE_ID_SYDNEY}-{BRANCH_DATE_STAMP}"
SIMPLE_INFO = {"url": EXAMPLE_URL, "selectors": {}, "file": "consulates/x.md"}
NY_INFO = {
    "url": EXAMPLE_URL,
    "file": CONSULATE_FILE,
    "selectors": {"address": {"pattern": "Address"}},
}
ORIGINAL_MARKDOWN = (
    "## Contact\n\n"
    "*Address:*  \nOld Address\n\n"
    "*Phone:*  \nOld Phone\n\n"
    "*Page last updated: January 01, 2025*\n"
)
OLD_FILE_CONTENT = b"*Address:*  \nOld\n\n*Page last updated: Jan 01, 2025*"
FAKE_CONSULATES = {
    "a": {"url": "u", "file": "f", "selectors": {}},
    "b": {"url": "u", "file": "f", "selectors": {}},
}

EXPECTED_ADDRESS = "Address: 123 Main St Seattle WA 98001"
EXPECTED_PHONE = "Call us: +1 (206) 555-1212"
EXPECTED_PHONE_FALLBACK = "Call us fallback: +1 (425) 555-0000"
NEW_ADDRESS = "New Address"
NEW_MARKDOWN = "new markdown"
UNCHANGED_MARKDOWN = "same markdown"
UPDATE_BRANCH = "update-branch"
SYDNEY_CHANGES = {"phone": "+61 2 1234 5678", "email": "info@example.com"}


class TestRequireEnv:
    @patch.dict(os.environ, {"REQUIRED_VAR": "present"})
    def test_returns_value(self):
        assert sut._require_env("REQUIRED_VAR") == "present"

    def test_raises_when_missing(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("MISSING_VAR", None)
            with pytest.raises(ValueError, match="MISSING_VAR not set"):
                sut._require_env("MISSING_VAR")


class TestGetWebsiteContent:
    def setUp(self):
        self.response = Mock()
        self.response.text = EXAMPLE_HTML
        self.response.raise_for_status = Mock()

    @patch.object(sut.requests, "get")
    def test_success(self, get_mock):
        self.setUp()
        get_mock.return_value = self.response

        soup = sut.get_website_content(EXAMPLE_URL)

        assert isinstance(soup, BeautifulSoup)
        assert "Hello" in list(soup.stripped_strings)
        get_mock.assert_called_once_with(
            EXAMPLE_URL,
            headers={"User-Agent": sut.USER_AGENT},
            timeout=sut.REQUEST_TIMEOUT_SECONDS,
        )

    @patch.object(sut.requests, "get", side_effect=RuntimeError("boom"))
    def test_failure_returns_none(self, _get_mock):
        assert sut.get_website_content(EXAMPLE_URL) is None


class TestCheckUpdates:
    def setUp(self):
        html = f"""
        <div>
          <p>{EXPECTED_ADDRESS}</p>
          <p>{EXPECTED_PHONE}</p>
          <p>{EXPECTED_PHONE_FALLBACK}</p>
        </div>
        """
        self.soup = BeautifulSoup(html, "html.parser")
        self.info = {
            "selectors": {
                "address": {"pattern": r"Seattle"},
                "phone": {"pattern": r"\(206\)\s*555-1212|\(425\)\s*555-0000"},
            }
        }

    def test_returns_first_match_per_field(self):
        self.setUp()

        changes = sut.check_updates(self.soup, self.info)

        assert changes == {
            "address": EXPECTED_ADDRESS,
            "phone": EXPECTED_PHONE,
        }


class TestUpdateFileContent:
    def test_updates_matching_fields_and_page_date(self):
        updated = sut.update_file_content(
            ORIGINAL_MARKDOWN,
            {"address": "New Address", "phone": "New Phone"},
            CURRENT_DATE,
        )

        assert "*Address:*  \nNew Address" in updated
        assert "*Phone:*  \nNew Phone" in updated
        assert f"*Page last updated: {CURRENT_DATE}*" in updated


class TestDeleteBranchIfExists:
    def setUp(self):
        self.ref = Mock()
        self.repo = Mock()
        self.repo.get_git_ref.return_value = self.ref

    def test_deletes_ref(self):
        self.setUp()

        sut._delete_branch_if_exists(self.repo, "my-branch")

        self.repo.get_git_ref.assert_called_once_with("heads/my-branch")
        self.ref.delete.assert_called_once_with()


class TestCreateUpdateBranch:
    def setUp(self):
        self.repo = Mock()
        self.repo.get_branch.return_value = SimpleNamespace(
            commit=SimpleNamespace(sha=MAIN_SHA),
        )

    @patch.object(sut, "datetime")
    @patch.object(sut, "_delete_branch_if_exists")
    def test_deletes_then_creates(self, delete_mock, datetime_mock):
        self.setUp()
        datetime_mock.now.return_value.strftime.return_value = BRANCH_DATE_STAMP

        branch = sut._create_update_branch(self.repo, CONSULATE_ID_NY)

        assert branch == BRANCH_NAME_NY
        delete_mock.assert_called_once_with(self.repo, BRANCH_NAME_NY)
        self.repo.create_git_ref.assert_called_once_with(
            ref=f"refs/heads/{BRANCH_NAME_NY}",
            sha=MAIN_SHA,
        )


class TestOpenPullRequest:
    def setUp(self):
        self.repo = Mock()

    def test_builds_expected_payload(self):
        self.setUp()

        sut._open_pull_request(
            self.repo,
            consulate_id=CONSULATE_ID_SYDNEY,
            changes=SYDNEY_CHANGES,
            branch_name=BRANCH_NAME_SYDNEY,
        )

        self.repo.create_pull.assert_called_once()
        kwargs = self.repo.create_pull.call_args.kwargs
        assert kwargs["title"] == f"Update {CONSULATE_ID_SYDNEY} consulate information"
        assert kwargs["head"] == BRANCH_NAME_SYDNEY
        assert kwargs["base"] == sut.BASE_BRANCH
        for field, value in SYDNEY_CHANGES.items():
            assert f"- {field}: {value}" in kwargs["body"]


class TestProcessConsulate:
    def setUp(self):
        self.repo = Mock()

    @patch.object(sut, "get_website_content", return_value=None)
    def test_stops_when_no_page(self, _gwc_mock):
        self.setUp()

        sut._process_consulate(self.repo, "x", SIMPLE_INFO, CURRENT_DATE)

        self.repo.get_contents.assert_not_called()

    @patch.object(sut, "check_updates", return_value={})
    @patch.object(sut, "get_website_content")
    def test_stops_when_no_changes(self, _gwc_mock, _cu_mock):
        self.setUp()

        sut._process_consulate(self.repo, "x", SIMPLE_INFO, CURRENT_DATE)

        self.repo.get_contents.assert_not_called()

    @patch.object(sut, "_open_pull_request")
    @patch.object(sut, "_create_update_branch", return_value=UPDATE_BRANCH)
    @patch.object(sut, "update_file_content", return_value=NEW_MARKDOWN)
    @patch.object(sut, "check_updates", return_value={"address": NEW_ADDRESS})
    @patch.object(sut, "get_website_content")
    def test_full_flow(self, _gwc_mock, _cu_mock, _ufc_mock, _cub_mock, open_pr_mock):
        self.setUp()
        file_obj = SimpleNamespace(decoded_content=OLD_FILE_CONTENT, sha=FILE_SHA)
        self.repo.get_contents.return_value = file_obj

        sut._process_consulate(self.repo, CONSULATE_ID_NY, NY_INFO, CURRENT_DATE)

        self.repo.update_file.assert_called_once_with(
            path=CONSULATE_FILE,
            message=f"Update {CONSULATE_ID_NY} consulate information",
            content=NEW_MARKDOWN,
            sha=FILE_SHA,
            branch=UPDATE_BRANCH,
        )
        open_pr_mock.assert_called_once_with(
            self.repo,
            CONSULATE_ID_NY,
            {"address": NEW_ADDRESS},
            UPDATE_BRANCH,
        )

    @patch.object(sut, "_create_update_branch")
    @patch.object(sut, "update_file_content", return_value=UNCHANGED_MARKDOWN)
    @patch.object(sut, "check_updates", return_value={"address": "Still same"})
    @patch.object(sut, "get_website_content")
    def test_skips_when_content_unchanged(self, _gwc_mock, _cu_mock, _ufc_mock, create_branch_mock):
        self.setUp()
        file_obj = SimpleNamespace(decoded_content=UNCHANGED_MARKDOWN.encode("utf-8"), sha=FILE_SHA)
        self.repo.get_contents.return_value = file_obj

        sut._process_consulate(self.repo, CONSULATE_ID_NY, NY_INFO, CURRENT_DATE)

        create_branch_mock.assert_not_called()
        self.repo.update_file.assert_not_called()


class TestMain:
    @patch.object(sut, "_process_consulate")
    @patch.object(sut, "CONSULATES", FAKE_CONSULATES)
    @patch.object(sut, "Github")
    @patch.dict(os.environ, {"GITHUB_TOKEN": "token", "GITHUB_REPOSITORY": "owner/repo"})
    def test_processes_all_consulates(self, github_mock, process_mock):
        fake_repo = Mock()
        github_mock.return_value.get_repo.return_value = fake_repo

        sut.main()

        assert process_mock.call_count == 2
