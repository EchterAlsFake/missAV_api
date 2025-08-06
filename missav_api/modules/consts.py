import re

headers = {
    "Referer": "https://www.missav.ws",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.1"
}


regex_title = re.compile(r'<h1 class="text-base lg:text-lg text-nord6">(.*?)</h1>')
regex_video_code = re.compile(r'<span class="font-medium">(.*?)</span>')
regex_publish_date = re.compile(r'class="font-medium">(.*?)</time>')
regex_thumbnail = re.compile(r'og:image" content="(.*?)cover-n.jpg')
regex_m3u8_js = re.compile(r"'m3u8(.*?)video")