import os
import logging
import traceback

from base_api import BaseCore
from functools import cached_property
from base_api.modules import consts as bs_consts
from base_api.modules.progress_bars import Callback

try:
    from modules.consts import *

except (ModuleNotFoundError, ImportError):
    from .modules.consts import *

bs_consts.HEADERS = HEADERS
core = BaseCore()
logging.basicConfig(format='%(name)s %(levelname)s %(asctime)s %(message)s', datefmt='%I:%M:%S %p')
logger = logging.getLogger("MISSAV API")
logger.setLevel(logging.DEBUG)

def disable_logging():
    logger.setLevel(logging.CRITICAL)


class Video:
    def __init__(self, url: str) -> None:
        self.url = url
        self.content = core.fetch(url)

    @cached_property
    def title(self) -> str:
        """Returns the title of the video. Language depends on the URL language"""
        return regex_title.search(self.content).group(1)

    @cached_property
    def video_code(self) -> str:
        """Returns the specific video code"""
        return regex_video_code.search(self.content).group(1)

    @cached_property
    def publish_date(self) -> str:
        """Returns the publication date of the video"""
        return regex_publish_date.search(self.content).group(1)

    @cached_property
    def m3u8_base_url(self) -> str:
        """Returns the m3u8 base URL (master playlist)"""
        javascript_content = regex_m3u8_js.search(self.content).group(1)
        url_parts = javascript_content.split("|")[::-1]
        logging.debug(f"Constructing HLS URL from: {url_parts}")
        url = f"{url_parts[1]}://{url_parts[2]}.{url_parts[3]}/{url_parts[4]}-{url_parts[5]}-{url_parts[6]}-{url_parts[7]}-{url_parts[8]}/playlist.m3u8"
        logging.debug(f"Final URL: {url}")
        return url


    def get_segments_(self, quality: str) -> list:
        """Returns the list of HLS segments for a given quality"""
        return core.get_segments(quality=quality, m3u8_url_master=self.m3u8_base_url)

    def download(self, quality: str, downloader: str, path: str = "./", no_title=False,
                 callback=Callback.text_progress_bar) -> bool:
        """Downloads the video from HLS"""
        if no_title is False:
            path = os.path.join(path, self.title + ".mp4")

        try:
            core.download(video=self, quality=quality, path=path, callback=callback, downloader=downloader)
            return True

        except Exception:
            error = traceback.format_exc()
            logger.error(error)
            return False


class Client:

    @classmethod
    def get_video(cls, url: str) -> Video:
        """Returns the video object"""
        return Video(url)
