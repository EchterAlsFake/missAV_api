from ..missav_api import Client


client = Client()
video = client.get_video("https://missav.com/de/fc2-ppv-4542556")

def test_video_attributes():
    assert isinstance(video.title, str)
    assert isinstance(video.publish_date, str)
    assert isinstance(video.m3u8_base_url, str)
    assert isinstance(video.video_code, str)

def test_download():
    assert video.download(quality="worst", downloader="threaded") is True