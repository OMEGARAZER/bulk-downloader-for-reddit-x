#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import Mock

import pytest

from bdfr.resource import Resource
from bdfr.site_downloaders.imgur import Imgur


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected_hashes"),
    (
        ("https://imgur.com/a/xWZsDDP", ("f551d6e6b0fef2ce909767338612e31b",)),
        ("https://imgur.com/gallery/IjJJdlC", ("740b006cf9ec9d6f734b6e8f5130bdab",)),
        ("https://imgur.com/gallery/IjJJdlC/", ("740b006cf9ec9d6f734b6e8f5130bdab",)),
        (
            "https://imgur.com/a/dcc84Gt",
            (
                "cf1158e1de5c3c8993461383b96610cf",
                "28d6b791a2daef8aa363bf5a3198535d",
                "248ef8f2a6d03eeb2a80d0123dbaf9b6",
                "029c475ce01b58fdf1269d8771d33913",
            ),
        ),
        (
            "https://imgur.com/a/eemHCCK",
            (
                "9cb757fd8f055e7ef7aa88addc9d9fa5",
                "b6cb6c918e2544e96fb7c07d828774b5",
                "fb6c913d721c0bbb96aa65d7f560d385",
            ),
        ),
        ("https://o.imgur.com/jZw9gq2.jpg", ("6d6ea9aa1d98827a05425338afe675bc",)),
        ("https://i.imgur.com/lFJai6i.gifv", ("01a6e79a30bec0e644e5da12365d5071",)),
        ("https://i.imgur.com/ywSyILa.gifv?", ("56d4afc32d2966017c38d98568709b45",)),
        ("https://imgur.com/ubYwpbk.GIFV", ("d4a774aac1667783f9ed3a1bd02fac0c",)),
        ("https://i.imgur.com/j1CNCZY.gifv", ("ed63d7062bc32edaeea8b53f876a307c",)),
        ("https://i.imgur.com/uTvtQsw.gifv", ("46c86533aa60fc0e09f2a758513e3ac2",)),
        ("https://i.imgur.com/OGeVuAe.giff", ("77389679084d381336f168538793f218",)),
        ("https://i.imgur.com/OGeVuAe.gift", ("77389679084d381336f168538793f218",)),
        ("https://i.imgur.com/3SKrQfK.jpg?1", ("aa299e181b268578979cad176d1bd1d0",)),
        ("https://i.imgur.com/cbivYRW.jpg?3", ("7ec6ceef5380cb163a1d498c359c51fd",)),
        ("http://i.imgur.com/s9uXxlq.jpg?5.jpg", ("338de3c23ee21af056b3a7c154e2478f",)),
        ("http://i.imgur.com/s9uXxlqb.jpg", ("338de3c23ee21af056b3a7c154e2478f",)),
        ("https://i.imgur.com/2TtN68l_d.webp", ("6569ab9ad9fa68d93f6b408f112dd741",)),
        ("https://imgur.com/a/1qzfWtY/gifv", ("65fbc7ba5c3ed0e3af47c4feef4d3735",)),
        ("https://imgur.com/a/1qzfWtY/mp4", ("65fbc7ba5c3ed0e3af47c4feef4d3735",)),
        ("https://imgur.com/a/1qzfWtY/spqr", ("65fbc7ba5c3ed0e3af47c4feef4d3735",)),
        ("https://i.imgur.com/expO7Rc.gifv", ("e309f98158fc98072eb2ae68f947f421",)),
    ),
)
def test_find_resources(test_url: str, expected_hashes: list[str]):
    mock_download = Mock()
    mock_download.url = test_url
    downloader = Imgur(mock_download)
    results = downloader.find_resources()
    assert all([isinstance(res, Resource) for res in results])
    [res.download() for res in results]
    hashes = set([res.hash.hexdigest() for res in results])
    assert hashes == set(expected_hashes)
