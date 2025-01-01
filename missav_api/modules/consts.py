import re

HEADERS = {
    "Referer": "https://missav.com/dm9/en",
}


regex_title = re.compile(r'<h1 class="text-base lg:text-lg text-nord6">(.*?)</h1>')
regex_video_code = re.compile(r'<span class="font-medium">(.*?)</span>')
regex_publish_date = re.compile(r'class="font-medium">(.*?)</time>')
regex_m3u8_js = re.compile(r"'m3u8(.*?)video")