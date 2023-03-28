from abc import ABC, abstractmethod

from bdfrx.site_downloaders.base_downloader import BaseDownloader


class BaseFallbackDownloader(BaseDownloader, ABC):
    @staticmethod
    @abstractmethod
    def can_handle_link(url: str) -> bool:
        """Returns whether the fallback downloader can download this link"""
        raise NotImplementedError
