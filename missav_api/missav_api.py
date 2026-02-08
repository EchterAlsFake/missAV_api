import os
import logging
import threading
import time
import hmac
import hashlib

from base_api import BaseCore
from bs4 import BeautifulSoup
from urllib.parse import quote
from functools import cached_property
from typing import Optional, Generator, List
from base_api.base import setup_logger, Helper
from base_api.modules.config import RuntimeConfig
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_HOST = "client-rapi-missav.recombee.com"
DATABASE_ID = "missav-default"
PUBLIC_TOKEN = "Ikkg568nlM51RHvldlPvc2GzZPE9R4XGzaH9Qj4zK9npbbbTly1gj9K4mgRn0QlV"
# You can change these if you want

try:
    import lxml
    parser = "lxml"

except (ModuleNotFoundError, ImportError):
    parser = "html.parser"

try:
    from modules.consts import *

except (ModuleNotFoundError, ImportError):
    from .modules.consts import *


def _sign_path(path: str, token: str) -> str:
    """
    Reproduce _signUrl(path) from the JS:
      1) build "/{databaseId}{path}?frontend_timestamp=UNIX"
      2) HMAC-SHA1 that string with the public token (text)
      3) append &frontend_sign=hexdigest
    """
    ts = int(time.time())
    unsigned = f"/{DATABASE_ID}{path}"
    if "?" in unsigned:
        unsigned += f"&frontend_timestamp={ts}"
    else:
        unsigned += f"?frontend_timestamp={ts}"
    signature = hmac.new(token.encode("utf-8"),
                         unsigned.encode("utf-8"),
                         hashlib.sha1).hexdigest()
    return unsigned + f"&frontend_sign={signature}"

def _post(core, path: str, json_body: dict, timeout=9):
    signed_path = _sign_path(path, PUBLIC_TOKEN)
    url = f"https://{BASE_HOST}{signed_path}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    resp = core.fetch(url, json=json_body, headers=headers, timeout=timeout, method="POST", get_response=True)
    return resp.json()


class ErrorVideo:
    """Drop-in-ish stand-in that raises when accessed."""
    def __init__(self, url: str, err: Exception):
        self.url = url
        self._err = err

    def __getattr__(self, _):
        # Any attribute access surfaces the original error
        raise self._err


class Video:
    def __init__(self, url: str, core: Optional[BaseCore] = None) -> None:
        self.url = url
        self.core = core
        self.core.enable_logging(level=logging.DEBUG)
        self.logger = setup_logger(name="MISSAV API - [Video]", log_file=None, level=logging.CRITICAL)
        self.content = self.core.fetch(url)
        self.soup = BeautifulSoup(self.content, parser)
        _meta_div = self.soup.find("div", class_="space-y-2")
        self.meta_divs = _meta_div.find_all("div", class_="text-secondary")

    def enable_logging(self, level, log_file: str = None):
        self.logger = setup_logger(name="MISSAV API - [Video]", log_file=log_file, level=level)

    @cached_property
    def title(self) -> str:
        """Returns the title of the video. Language depends on the URL language"""
        return self.soup.find("h1", class_="text-base lg:text-lg text-nord6").text.strip()

    @cached_property
    def publish_date(self) -> str:
        """Returns the publish date of the video"""
        return self.meta_divs[0].find("time", class_="font-medium").text.strip()

    @cached_property
    def video_code(self) -> str:
        """Returns the specific video code"""
        return self.meta_divs[1].find("span", class_="font-medium").text.strip()

    @cached_property
    def title_original_japanese(self) -> str:
        """Returns the original title of the video"""
        try:
            return self.meta_divs[2].find("span", class_="font-medium").text.strip()

        except IndexError:
            return ""

    @cached_property
    def genres(self) -> List[str]:
        """Returns the genres of the video"""
        try:
            genres = []
            a_tags = self.meta_divs[3].find_all("a")
            for a_tag in a_tags:
                genres.append(a_tag.text.strip())

            return genres

        except IndexError:
            return []


    @cached_property
    def series(self) -> str:
        """Returns the series of the video"""
        try:
            return self.meta_divs[4].find("a").text.strip()

        except IndexError:
            return ""

    @cached_property
    def manufacturer(self) -> str:
        """Returns the manufacturer of the video"""
        try:
            return self.meta_divs[5].find("a").text.strip()

        except IndexError:
            return ""

    @cached_property
    def etiquette(self) -> str:
        """Returns the etiquette of the video"""
        try:
            return self.meta_divs[6].find("a").text.strip()

        except IndexError:
            return ""

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
        return self.core.get_segments(quality=quality, m3u8_url_master=self.m3u8_base_url)

    def download(self, quality, path="./", callback=None, no_title=False, remux: bool = False,
                 callback_remux=None, start_segment: int = 0, stop_event: Optional[threading.Event] = None,
                 segment_state_path: Optional[str] = None, segment_dir: Optional[str] = None,
                 return_report: bool = False, cleanup_on_stop: bool = True, keep_segment_dir: bool = False
                 ) -> bool:
        """
        :param callback:
        :param quality:
        :param path:
        :param no_title:
        :param remux:
        :param callback_remux:
        :param start_segment:
        :param stop_event:
        :param segment_state_path:
        :param segment_dir:
        :param return_report:
        :param cleanup_on_stop:
        :param keep_segment_dir:
        :return:
        """
        if not no_title:
            path = os.path.join(path, f"{self.title}.mp4")

        return self.core.download(video=self, quality=quality, path=path, callback=callback, remux=remux,
                           callback_remux=callback_remux, start_segment=start_segment, stop_event=stop_event,
                           segment_state_path=segment_state_path, segment_dir=segment_dir, return_report=return_report,
                           cleanup_on_stop=cleanup_on_stop, keep_segment_dir=keep_segment_dir)


class Client(Helper):
    def __init__(self, core: Optional[BaseCore] = None):
        super(Client, self).__init__(core=core, video=Video)
        self.core = core or BaseCore(config=RuntimeConfig())
        self.core.config.use_http2 = False # Missav doesn't support http2
        self.core.initialize_session()
        self.core.session.headers.update(headers)

    def get_video(self, url: str) -> Video:
        """Returns the video object"""
        return Video(url, core=self.core)

    def search(self, query: str, video_count: int = 50, max_workers: int = None) -> Generator[Video, None, None]:
        """
        Mirrors: POST /search/users/{userId}/items/
        Body fields follow the snippet’s Recombee client (searchQuery, count, scenario, filter, booster, logic, etc.)
        """
        return_properties = True
        user_id = "anonymous"

        path = f"/search/users/{quote(user_id, safe='')}/items/"
        body = {
            "searchQuery": query,
            "count": video_count,
            "cascadeCreate": True,
            "returnProperties": return_properties,
        }

        body = {k: v for k, v in body.items() if v is not None}
        data = _post(path=path, json_body=body, timeout=9, core=self.core)
        videos = data.get("recomms", [])
        video_urls = []
        for video in videos:
            video_urls.append(f"https://missav.ws/en/{video['id']}")

        max_workers = max_workers or self.core.config.videos_concurrency

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._make_video_safe, url) for url in video_urls]
            for fut in as_completed(futures):
                yield fut.result()
