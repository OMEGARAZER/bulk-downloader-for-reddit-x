#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.direct import Direct


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected_hash"),
    (
        ("https://i.redd.it/q6ebualjxzea1.jpg", "6ec154859c777cb401132bb991cb3635"),
        (
            "https://file-examples.com/wp-content/uploads/2017/11/file_example_MP3_700KB.mp3",
            "3caa342e241ddb7d76fd24a834094101",
        ),
    ),
)
def test_download_resource(test_url: str, expected_hash: str):
    mock_submission = Mock()
    mock_submission.url = test_url
    test_site = Direct(mock_submission)
    resources = test_site.find_resources()
    assert len(resources) == 1
    assert isinstance(resources[0], Resource)
    resources[0].download()
    assert resources[0].hash.hexdigest() == expected_hash
