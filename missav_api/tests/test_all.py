from ..missav_api import Client


client = Client()
video = client.get_video("https://missav.ws/dm13/de/fc2-ppv-2777644")

def test_video_attributes():
    assert isinstance(video.title, str)
    assert isinstance(video.publish_date, str)
    assert isinstance(video.m3u8_base_url, str)
    assert isinstance(video.video_code, str)
    assert isinstance(video.thumbnail, str)

def test_search():
    search = client.search("stepdaughter", video_count=10)
    for video in search:
        assert isinstance(video.title, str)

