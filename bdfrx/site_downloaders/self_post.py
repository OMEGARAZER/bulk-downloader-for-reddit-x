import logging
from typing import Optional

from praw.models import Submission

from bdfrx.resource import Resource
from bdfrx.site_authenticator import SiteAuthenticator
from bdfrx.site_downloaders.base_downloader import BaseDownloader

logger = logging.getLogger(__name__)


class SelfPost(BaseDownloader):
    def __init__(self, post: Submission) -> None:
        super().__init__(post)

    def find_resources(self, authenticator: Optional[SiteAuthenticator] = None) -> list[Resource]:
        out = Resource(self.post, self.post.url, lambda: None, ".txt")
        out.content = self.export_to_string().encode("utf-8")
        out.create_hash()
        return [out]

    def export_to_string(self) -> str:
        """Self posts are formatted here"""
        return (
            "## ["
            + self.post.fullname
            + "]("
            + self.post.url
            + ")\n"
            + self.post.selftext
            + "\n\n---\n\n"
            + "submitted to [r/"
            + self.post.subreddit.title
            + "](https://www.reddit.com/r/"
            + self.post.subreddit.title
            + ") by [u/"
            + (self.post.author.name if self.post.author else "DELETED")
            + "](https://www.reddit.com/user/"
            + (self.post.author.name if self.post.author else "DELETED")
            + ")"
        )
