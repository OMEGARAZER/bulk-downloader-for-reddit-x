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
    def pull_lever(url: str) -> type[BaseDownloader]:  # noqa: PLR0911,PLR0912
        sanitised_url = DownloadFactory.sanitise_url(url).lower()
        if re.match(r"(i\.|m\.|o\.)?imgur", sanitised_url):
            return Imgur
        if re.match(r"(i\.|thumbs\d\.|v\d\.)?(redgifs|gifdeliverynetwork)", sanitised_url):
            return Redgifs
        if re.match(r"(thumbs\.|giant\.)?gfycat\.", sanitised_url):
            return Gfycat
        if re.match(r".*/.*\.[a-zA-Z34]{3,4}(\?[\w;&=]*)?$", sanitised_url) and not DownloadFactory.is_web_resource(
            sanitised_url,
        ):
            return Direct
        if re.match(r"erome\.com.*", sanitised_url):
            return Erome
        if re.match(r"delayforreddit\.com", sanitised_url):
            return DelayForReddit
        if re.match(r"reddit\.com/gallery/.*", sanitised_url) or re.match(r"patreon\.com.*", sanitised_url):
            return Gallery
        if re.match(r"reddit\.com/r/", sanitised_url):
            return SelfPost
        if re.match(r"(m\.)?youtu\.?be", sanitised_url):
            return Youtube
        if re.match(r"i\.redd\.it.*", sanitised_url):
            return Direct
        if re.match(r"v\.redd\.it.*", sanitised_url):
            return VReddit
        if re.match(r"pornhub\.com.*", sanitised_url):
            return PornHub
        if re.match(r"vidble\.com", sanitised_url):
            return Vidble
        if YtdlpFallback.can_handle_link(sanitised_url):
            return YtdlpFallback
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
