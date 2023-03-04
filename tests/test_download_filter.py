#!/usr/bin/env python3

from unittest.mock import MagicMock

import pytest

from bdfrx.download_filter import DownloadFilter
from bdfrx.resource import Resource


@pytest.fixture()
def download_filter() -> DownloadFilter:
    return DownloadFilter(["mp4", "mp3"], ["test.com", "reddit.com", "img.example.com"])


@pytest.mark.parametrize(
    ("test_extension", "expected"),
    (
        (".mp4", False),
        (".avi", True),
        (".random.mp3", False),
        ("mp4", False),
    ),
)
def test_filter_extension(test_extension: str, expected: bool, download_filter: DownloadFilter):
    result = download_filter._check_extension(test_extension)
    assert result == expected


@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        ("test.mp4", True),
        ("http://reddit.com/test.mp4", False),
        ("http://reddit.com/test.gif", False),
        ("https://www.example.com/test.mp4", True),
        ("https://www.example.com/test.png", True),
        ("https://i.example.com/test.png", True),
        ("https://img.example.com/test.png", False),
        ("https://i.test.com/test.png", False),
    ),
)
def test_filter_domain(test_url: str, expected: bool, download_filter: DownloadFilter):
    result = download_filter._check_domain(test_url)
    assert result == expected


@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        ("test.mp4", False),
        ("test.gif", True),
        ("https://www.example.com/test.mp4", False),
        ("https://www.example.com/test.png", True),
        ("http://reddit.com/test.mp4", False),
        ("http://reddit.com/test.gif", False),
    ),
)
def test_filter_all(test_url: str, expected: bool, download_filter: DownloadFilter):
    test_resource = Resource(MagicMock(), test_url, lambda: None)
    result = download_filter.check_resource(test_resource)
    assert result == expected


@pytest.mark.parametrize(
    "test_url",
    (
        "test.mp3",
        "test.mp4",
        "http://reddit.com/test.mp4",
        "t",
    ),
)
def test_filter_empty_filter(test_url: str):
    download_filter = DownloadFilter()
    test_resource = Resource(MagicMock(), test_url, lambda: None)
    result = download_filter.check_resource(test_resource)
    assert result
