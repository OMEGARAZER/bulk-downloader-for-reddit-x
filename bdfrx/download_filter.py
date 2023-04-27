import logging
import re

from bdfrx.resource import Resource

logger = logging.getLogger(__name__)


class DownloadFilter:
    def __init__(self, excluded_extensions: list[str] = None, excluded_domains: list[str] = None) -> None:
        self.excluded_extensions = excluded_extensions
        self.excluded_domains = excluded_domains

    def check_url(self, url: str) -> bool:
        """Return whether a URL is allowed or not"""
        if not self._check_extension(url) or not self._check_domain(url):
            return False
        return True

    def check_resource(self, res: Resource) -> bool:
        if not self._check_extension(res.extension) or not self._check_domain(res.url):
            return False
        return True

    def _check_extension(self, resource_extension: str) -> bool:
        if not self.excluded_extensions:
            return True
        combined_extensions = "|".join(self.excluded_extensions)
        pattern = re.compile(rf".*({combined_extensions})$")
        if pattern.match(resource_extension):
            logger.log(9, f"Url extension {resource_extension!r} matched with {pattern!r}")
            return False
        return True

    def _check_domain(self, url: str) -> bool:
        if not self.excluded_domains:
            return True
        combined_domains = "|".join(self.excluded_domains)
        pattern = re.compile(rf"https?://.*({combined_domains}).*")
        if pattern.match(url):
            logger.log(9, f"Url domain {url!r} matched with {pattern!r}")
            return False
        return True
