import pytest
from ..missav_api import Client


@pytest.mark.asyncio
async def test_video_attributes():
    client = Client()
    video = await client.get_video("https://missav.com/de/fc2-ppv-4542556")

    assert isinstance(video.title, str)
    assert isinstance(video.publish_date, str)
    assert isinstance(video.m3u8_base_url, str)
    assert isinstance(video.video_code, str)
    assert isinstance(video.thumbnail, str)
    assert await video.download(quality="worst", downloader="threaded") is True
