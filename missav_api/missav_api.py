import os
import logging
import traceback

from base_api import BaseCore
from functools import cached_property
from base_api.base import setup_logger
from base_api.modules.progress_bars import Callback
from base_api.modules import config

try:
    from modules.consts import *

except (ModuleNotFoundError, ImportError):
    from .modules.consts import *

HEADERS = HEADERS
core = BaseCore()


def refresh_core(custom_config=None, enable_logging=False, level=None, log_file: str = None):
    global core
    cfg = custom_config or config.config
    cfg.headers = HEADERS
    core = BaseCore(cfg)

    if enable_logging:
        core.enable_logging(log_file=log_file, level=level)

refresh_core()

class Video:
    def __init__(self, url: str) -> None:
        self.url = url
        self.logger = setup_logger(name="MISSAV API - [Video]", log_file=None, level=logging.CRITICAL)
        self.content = core.fetch(url)

    def enable_logging(self, level, log_file: str = None):
        self.logger = setup_logger(name="MISSAV API - [Video]", log_file=log_file, level=level)

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
        self.logger.debug(f"Constructing HLS URL from: {url_parts}")
        url = f"{url_parts[1]}://{url_parts[2]}.{url_parts[3]}/{url_parts[4]}-{url_parts[5]}-{url_parts[6]}-{url_parts[7]}-{url_parts[8]}/playlist.m3u8"
        self.logger.debug(f"Final URL: {url}")
        return url

    @cached_property
    def thumbnail(self) -> str:
        """Returns the main video thumbnail"""
        return f"{regex_thumbnail.search(self.content).group(1)}cover-n.jpg"

    def get_segments(self, quality: str) -> list:
        """Returns the list of HLS segments for a given quality"""
        return core.get_segments(quality=quality, m3u8_url_master=self.m3u8_base_url)

    def download(self, quality: str, downloader: str, path: str = "./", no_title=False,
                 callback=Callback.text_progress_bar) -> bool:
        """Downloads the video from HLS"""
        if no_title is False:
            path = os.path.join(path, core.truncate(core.strip_title(self.title)) + ".mp4")

        try:
            core.download(video=self, quality=quality, path=path, callback=callback, downloader=downloader)
            return True

        except Exception:
            error = traceback.format_exc()
            self.logger.error(error)
            return False


class Client:

    @classmethod
    def get_video(cls, url: str) -> Video:
        """Returns the video object"""
        return Video(url)
