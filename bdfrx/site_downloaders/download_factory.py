#!/usr/bin/env python3

import re
import urllib.parse

from bdfrx.exceptions import NotADownloadableLinkError
from bdfrx.site_downloaders.base_downloader import BaseDownloader
from bdfrx.site_downloaders.delay_for_reddit import DelayForReddit
from bdfrx.site_downloaders.direct import Direct
from bdfrx.site_downloaders.erome import Erome
from bdfrx.site_downloaders.fallback_downloaders.ytdlp_fallback import YtdlpFallback
from bdfrx.site_downloaders.gallery import Gallery
from bdfrx.site_downloaders.gfycat import Gfycat
from bdfrx.site_downloaders.imgur import Imgur
from bdfrx.site_downloaders.pornhub import PornHub
from bdfrx.site_downloaders.redgifs import Redgifs
from bdfrx.site_downloaders.self_post import SelfPost
from bdfrx.site_downloaders.vidble import Vidble
from bdfrx.site_downloaders.vreddit import VReddit
from bdfrx.site_downloaders.youtube import Youtube


class DownloadFactory:
    @staticmethod
    def pull_lever(url: str) -> type[BaseDownloader]:
        sanitised_url = DownloadFactory.sanitise_url(url).lower()
        if re.match(r"(i\.|m\.|o\.)?imgur", sanitised_url):
            return Imgur
        elif re.match(r"(i\.|thumbs\d\.|v\d\.)?(redgifs|gifdeliverynetwork)", sanitised_url):
            return Redgifs
        elif re.match(r"(thumbs\.|giant\.)?gfycat\.", sanitised_url):
            return Gfycat
        elif re.match(r".*/.*\.[a-zA-Z34]{3,4}(\?[\w;&=]*)?$", sanitised_url) and not DownloadFactory.is_web_resource(
            sanitised_url
        ):
            return Direct
        elif re.match(r"erome\.com.*", sanitised_url):
            return Erome
        elif re.match(r"delayforreddit\.com", sanitised_url):
            return DelayForReddit
        elif re.match(r"reddit\.com/gallery/.*", sanitised_url):
            return Gallery
        elif re.match(r"patreon\.com.*", sanitised_url):
            return Gallery
        elif re.match(r"reddit\.com/r/", sanitised_url):
            return SelfPost
        elif re.match(r"(m\.)?youtu\.?be", sanitised_url):
            return Youtube
        elif re.match(r"i\.redd\.it.*", sanitised_url):
            return Direct
        elif re.match(r"v\.redd\.it.*", sanitised_url):
            return VReddit
        elif re.match(r"pornhub\.com.*", sanitised_url):
            return PornHub
        elif re.match(r"vidble\.com", sanitised_url):
            return Vidble
        elif YtdlpFallback.can_handle_link(sanitised_url):
            return YtdlpFallback
        else:
            raise NotADownloadableLinkError(f"No downloader module exists for url {url}")

    @staticmethod
    def sanitise_url(url: str) -> str:
        beginning_regex = re.compile(r"\s*(www\.?)?")
        split_url = urllib.parse.urlsplit(url)
        split_url = split_url.netloc + split_url.path
        split_url = re.sub(beginning_regex, "", split_url)
        return split_url

    @staticmethod
    def is_web_resource(url: str) -> bool:
        web_extensions = (
            "asp",
            "aspx",
            "cfm",
            "cfml",
            "css",
            "htm",
            "html",
            "js",
            "php",
            "php3",
            "xhtml",
        )
        if re.match(rf"(?i).*/.*\.({'|'.join(web_extensions)})$", url):
            return True
        return False
