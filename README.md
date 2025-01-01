<h1 align="center">missAV API</h1> 

<div align="center">
    <a href="https://pepy.tech/project/missAV_api"><img src="https://static.pepy.tech/badge/missAV_api" alt="Downloads"></a>
    <a href="https://github.com/EchterAlsFake/missAV_api/workflows/"><img src="https://github.com/EchterAlsFake/missAV_api/workflows/CodeQL/badge.svg" alt="CodeQL Analysis"/></a>
    <a href="https://github.com/EchterAlsFake/missAV_api/workflows/"><img src="https://github.com/EchterAlsFake/missAV_api/actions/workflows/tests.yml/badge.svg" alt="API Tests"/></a>
</div>

# Description
missAV API is an API for missav.com. It allows you to download videos using HLS streaming

# Disclaimer
> [!IMPORTANT] 
> missAV API is in violation to the ToS of missav.com!
> If you are the website owner of missav.com, contact me at my E-Mail, and I'll take this repository immediately offline.
> EchterAlsFake@proton.me

> [!NOTE]
> This project was developed for my **[Porn Fetch](https://github.com/EchterAlsFake/Porn_Fetch)** project to support video downloading
> from missav. Therefore, this API only has very basic and limited functionality. If you want more features, I can extend this
> API, so don't hesitate to open an issue about it :)
# Quickstart

### Have a look at the [Documentation](https://github.com/EchterAlsFake/API_Docs/blob/master/Porn_APIs/missAV.md) for more details

- Install the library with `pip install missAV_api`


```python
from missav_api import Client
# Initialize a Client object
client = Client()

# Fetch a video
video_object = client.get_video("<insert_url_here>")

# Information from Video objects
print(video_object.title)
# Download the video

video_object.download(downloader="threaded", quality="best", path="your_output_path + filename")

# SEE DOCUMENTATION FOR MORE
```

# Changelog
See [Changelog](https://github.com/EchterAlsFake/missAV_api/blob/master/README/Changelog.md) for more details.

# Contribution
Do you see any issues or having some feature requests? Simply open an Issue or talk
in the discussions.

Pull requests are also welcome.

# License
Licensed under the [LGPLv3](https://www.gnu.org/licenses/lgpl-3.0.en.html) License
<br>Copyright (C) 2024-2025 Johannes Habel