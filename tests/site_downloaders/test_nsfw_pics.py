from unittest.mock import Mock

import pytest

from bdfrx.resource import Resource
from bdfrx.site_downloaders.nsfw_pics import NsfwPics


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        (
            "https://nsfw.pics/album/Test.l2t",  # Album
            {
                "https://nsfw.pics/image/OdfV",
                "https://nsfw.pics/image/ObUF",
                "https://nsfw.pics/image/OOV7",
                "https://nsfw.pics/image/OD71",
                "https://nsfw.pics/image/O6du",
            },
        ),
    ),
)
def test_get_album(test_url: str, expected: set[str]):
    results = NsfwPics._get_album_links(test_url)
    assert len(results) == len(expected)
    assert sorted(results) == sorted(expected)


@pytest.mark.online
@pytest.mark.parametrize(
    ("test_url", "expected"),
    (
        (
            "https://nsfw.pics/album/Test.l2t",  # Album
            {
                "https://i.nsfw.pics/b8007b506022132fe857eead3dc98a92.gif",
                "https://i.nsfw.pics/aa0541830d5d16743bca9bfb48e16b7b.gif",
                "https://i.nsfw.pics/b4afb5a33e68d3d74a547f62684cddc9.jpeg",
                "https://i.nsfw.pics/131ed0764342b570a338af37cdd75e3e.jpeg",
                "https://i.nsfw.pics/c447389dee315f5960eb29671fb56232.jpeg",
            },
        ),
        (
            "https://nsfw.pics/image/OdfV",  # Single image
            {"https://i.nsfw.pics/b8007b506022132fe857eead3dc98a92.gif"},
        ),
    ),
)
def test_get_links(test_url: str, expected: set[str]):
    results = NsfwPics._get_links(test_url)
    assert sorted(results) == sorted(expected)


@pytest.mark.online
@pytest.mark.slow
@pytest.mark.parametrize(
    ("test_url", "expected_hashes"),
    (
        (
            "https://nsfw.pics/album/Test.l2t",  # Album
            {
                "9ceac1e26c4799b0a6b7d5453a73f53b",
                "8ff9229c39ad5403e9859a21d5aec103",
                "907f92b1c295d5f84f4f64aacc960079",
                "1098edadc345ec948d37e1541ed867eb",
                "fb60e0a42a0f7f0929f5a5ae401a3518",
            },
        ),
        (
            "https://nsfw.pics/image/OdfV",  # Single image
            {"9ceac1e26c4799b0a6b7d5453a73f53b"},
        ),
    ),
)
def test_download_resources(test_url: str, expected_hashes: set[str]):
    mock_download = Mock()
    mock_download.url = test_url
    downloader = NsfwPics(mock_download)
    results = downloader.find_resources()
    assert all(isinstance(res, Resource) for res in results)
    [res.download() for res in results]
    hashes = {res.hash.hexdigest() for res in results}
    assert hashes == set(expected_hashes)
