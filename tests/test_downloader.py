#!/usr/bin/env python3
import logging
import re
from pathlib import Path
from unittest.mock import MagicMock, patch

import praw.models
import pytest

from bdfrx.__main__ import make_console_logging_handler
from bdfrx.configuration import Configuration
from bdfrx.connector import RedditConnector
from bdfrx.downloader import RedditDownloader


def add_console_handler():
    logging.getLogger().addHandler(make_console_logging_handler(3))


@pytest.fixture()
def args() -> Configuration:
    args = Configuration()
    args.time_format = "ISO"
    return args


@pytest.fixture()
def downloader_mock(args: Configuration):
    downloader_mock = MagicMock()
    downloader_mock.args = args
    downloader_mock._sanitise_subreddit_name = RedditConnector.sanitise_subreddit_name
    downloader_mock._split_args_input = RedditConnector.split_args_input
    downloader_mock.master_hash_list = {}
    return downloader_mock


@pytest.mark.parametrize(
    ("test_ids", "test_excluded", "expected_len"),
    (
        (("aaaaaa",), (), 1),
        (("aaaaaa",), ("aaaaaa",), 0),
        ((), ("aaaaaa",), 0),
        (("aaaaaa", "bbbbbb"), ("aaaaaa",), 1),
        (("aaaaaa", "bbbbbb", "cccccc"), ("aaaaaa",), 2),
    ),
)
@patch("bdfrx.site_downloaders.download_factory.DownloadFactory.pull_lever")
def test_excluded_ids(
    mock_function: MagicMock,
    test_ids: tuple[str],
    test_excluded: tuple[str],
    expected_len: int,
    downloader_mock: MagicMock,
):
    downloader_mock.excluded_submission_ids = test_excluded
    mock_function.return_value = MagicMock()
    mock_function.return_value.__name__ = "test"
    test_submissions = []
    for test_id in test_ids:
        mock = MagicMock()
        mock.id = test_id
        mock.subreddit.display_name.return_value = "https://www.example.com/"
        mock.__class__ = praw.models.Submission
        test_submissions.append(mock)
    downloader_mock.reddit_lists = [test_submissions]
    for submission in test_submissions:
        RedditDownloader._download_submission(downloader_mock, submission)
    assert mock_function.call_count == expected_len


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize("test_submission_id", ("m1hqw6",))
def test_mark_hard_link(
    test_submission_id: str, downloader_mock: MagicMock, tmp_path: Path, reddit_instance: praw.Reddit
):
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.args.make_hard_links = True
    downloader_mock.download_directory = tmp_path
    downloader_mock.args.folder_scheme = ""
    downloader_mock.args.file_scheme = "{POSTID}"
    downloader_mock.file_name_formatter = RedditConnector.create_file_name_formatter(downloader_mock)
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)
    original = Path(tmp_path, f"{test_submission_id}.png")

    RedditDownloader._download_submission(downloader_mock, submission)
    assert original.exists()

    downloader_mock.args.file_scheme = "test2_{POSTID}"
    downloader_mock.file_name_formatter = RedditConnector.create_file_name_formatter(downloader_mock)
    RedditDownloader._download_submission(downloader_mock, submission)
    test_file_1_stats = original.stat()
    test_file_2_inode = Path(tmp_path, f"test2_{test_submission_id}.png").stat().st_ino

    assert test_file_1_stats.st_nlink == 2
    assert test_file_1_stats.st_ino == test_file_2_inode


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(("test_submission_id", "test_creation_date"), (("ndzz50", 1621204841.0),))
def test_file_creation_date(
    test_submission_id: str,
    test_creation_date: float,
    downloader_mock: MagicMock,
    tmp_path: Path,
    reddit_instance: praw.Reddit,
):
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_directory = tmp_path
    downloader_mock.args.folder_scheme = ""
    downloader_mock.args.file_scheme = "{POSTID}"
    downloader_mock.file_name_formatter = RedditConnector.create_file_name_formatter(downloader_mock)
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)

    RedditDownloader._download_submission(downloader_mock, submission)

    for file_path in Path(tmp_path).iterdir():
        file_stats = Path(file_path).stat()
        assert file_stats.st_mtime == test_creation_date


def test_search_existing_files():
    results = RedditDownloader.scan_existing_files(Path())
    assert len(results.keys()) != 0


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(("test_submission_id", "test_hash"), (("m1hqw6", "a912af8905ae468e0121e9940f797ad7"),))
def test_download_submission_hash_exists(
    test_submission_id: str,
    test_hash: str,
    downloader_mock: MagicMock,
    reddit_instance: praw.Reddit,
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    add_console_handler()
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.folder_scheme = ""
    downloader_mock.args.no_dupes = True
    downloader_mock.file_name_formatter = RedditConnector.create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    downloader_mock.master_hash_list = {test_hash: None}
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)
    RedditDownloader._download_submission(downloader_mock, submission)
    folder_contents = list(tmp_path.iterdir())
    output = capsys.readouterr()
    assert not folder_contents
    assert re.search(r"Resource hash .*? downloaded elsewhere", output.out)


@pytest.mark.online
@pytest.mark.reddit
def test_download_submission_file_exists(
    downloader_mock: MagicMock, reddit_instance: praw.Reddit, tmp_path: Path, capsys: pytest.CaptureFixture
):
    add_console_handler()
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.folder_scheme = ""
    downloader_mock.file_name_formatter = RedditConnector.create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    submission = downloader_mock.reddit_instance.submission(id="m1hqw6")
    Path(tmp_path, "Arneeman_Metagaming isn't always a bad thing_m1hqw6.png").touch()
    RedditDownloader._download_submission(downloader_mock, submission)
    folder_contents = list(tmp_path.iterdir())
    output = capsys.readouterr()
    assert len(folder_contents) == 1
    assert "Arneeman_Metagaming isn't always a bad thing_m1hqw6.png from submission m1hqw6 already exists" in output.out


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(("test_submission_id", "expected_files_len"), (("ljyy27", 4),))
def test_download_submission(
    test_submission_id: str,
    expected_files_len: int,
    downloader_mock: MagicMock,
    reddit_instance: praw.Reddit,
    tmp_path: Path,
):
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.folder_scheme = ""
    downloader_mock.file_name_formatter = RedditConnector.create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)
    RedditDownloader._download_submission(downloader_mock, submission)
    folder_contents = list(tmp_path.iterdir())
    assert len(folder_contents) == expected_files_len


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(("test_submission_id", "min_score"), (("ljyy27", 1),))
def test_download_submission_min_score_above(
    test_submission_id: str,
    min_score: int,
    downloader_mock: MagicMock,
    reddit_instance: praw.Reddit,
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    add_console_handler()
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.folder_scheme = ""
    downloader_mock.args.min_score = min_score
    downloader_mock.file_name_formatter = RedditConnector.create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)
    RedditDownloader._download_submission(downloader_mock, submission)
    output = capsys.readouterr()
    assert "filtered due to score" not in output.out


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(("test_submission_id", "min_score"), (("ljyy27", 25),))
def test_download_submission_min_score_below(
    test_submission_id: str,
    min_score: int,
    downloader_mock: MagicMock,
    reddit_instance: praw.Reddit,
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    add_console_handler()
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.folder_scheme = ""
    downloader_mock.args.min_score = min_score
    downloader_mock.file_name_formatter = RedditConnector.create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)
    RedditDownloader._download_submission(downloader_mock, submission)
    output = capsys.readouterr()
    assert "filtered due to score" in output.out


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(("test_submission_id", "max_score"), (("ljyy27", 25),))
def test_download_submission_max_score_below(
    test_submission_id: str,
    max_score: int,
    downloader_mock: MagicMock,
    reddit_instance: praw.Reddit,
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    add_console_handler()
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.folder_scheme = ""
    downloader_mock.args.max_score = max_score
    downloader_mock.file_name_formatter = RedditConnector.create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)
    RedditDownloader._download_submission(downloader_mock, submission)
    output = capsys.readouterr()
    assert "filtered due to score" not in output.out


@pytest.mark.online
@pytest.mark.reddit
@pytest.mark.parametrize(("test_submission_id", "max_score"), (("ljyy27", 1),))
def test_download_submission_max_score_above(
    test_submission_id: str,
    max_score: int,
    downloader_mock: MagicMock,
    reddit_instance: praw.Reddit,
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    add_console_handler()
    downloader_mock.reddit_instance = reddit_instance
    downloader_mock.download_filter.check_url.return_value = True
    downloader_mock.args.folder_scheme = ""
    downloader_mock.args.max_score = max_score
    downloader_mock.file_name_formatter = RedditConnector.create_file_name_formatter(downloader_mock)
    downloader_mock.download_directory = tmp_path
    submission = downloader_mock.reddit_instance.submission(id=test_submission_id)
    RedditDownloader._download_submission(downloader_mock, submission)
    output = capsys.readouterr()
    assert "filtered due to score" in output.out
