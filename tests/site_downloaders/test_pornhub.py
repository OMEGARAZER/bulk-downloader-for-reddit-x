#!/usr/bin/env python3
# coding=utf-8

from unittest.mock import MagicMock

import pytest

from bdfr.exceptions import SiteDownloaderError
from bdfr.resource import Resource
from bdfr.site_downloaders.pornhub import PornHub


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test_url", "expected_hash"),
    (("https://www.pornhub.com/view_video.php?viewkey=ph6074c59798497", "ad52a0f4fce8f99df0abed17de1d04c7"),),
)
def test_hash_resources_good(test_url: str, expected_hash: str):
    test_submission = MagicMock()
    test_submission.url = test_url
    downloader = PornHub(test_submission)
    resources = downloader.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download()
    assert resources[0].hash.hexdigest() == expected_hash


@pytest.mark.online
@pytest.mark.parametrize("test_url", ("https://www.pornhub.com/view_video.php?viewkey=ph5ede121f0d3f8",))
def test_find_resources_good(test_url: str):
    test_submission = MagicMock()
    test_submission.url = test_url
    downloader = PornHub(test_submission)
    with pytest.raises(SiteDownloaderError):
        downloader.find_resources()
