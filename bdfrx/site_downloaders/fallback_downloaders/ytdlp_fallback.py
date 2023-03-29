import logging
from typing import Optional

from praw.models import Submission

from bdfrx.exceptions import NotADownloadableLinkError
from bdfrx.resource import Resource
from bdfrx.site_authenticator import SiteAuthenticator
from bdfrx.site_downloaders.fallback_downloaders.fallback_downloader import BaseFallbackDownloader
from bdfrx.site_downloaders.youtube import Youtube

logger = logging.getLogger(__name__)


class YtdlpFallback(BaseFallbackDownloader, Youtube):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        out = Resource(
            self.post,
            self.post.url,
            super()._download_video({}),
            super().get_video_attributes(self.post.url)["ext"],
        )
        return [out]

    @staticmethod
    def can_handle_link(url: str) -> bool:
        try:
            attributes = YtdlpFallback.get_video_attributes(url)
        except NotADownloadableLinkError:
            return False
        if attributes:
            return True
        return False
