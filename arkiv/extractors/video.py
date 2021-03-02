import os
import datetime
import logging
from contextlib import redirect_stderr

from youtube_dl import YoutubeDL
from youtube_dl.extractor import gen_extractor_classes
import requests
import bs4

from ..utils import profile

log = logging.getLogger(__name__)


@profile
def extract(url):
    log.info("extracting video data...")

    opts = {
        "quiet": True,
        "simulate": True,
        "forcejson": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "logtostderr": True,
    }

    # an awkward dance to get around the fact that youtube-dl does not
    # use a proper logger
    with open(os.devnull, "w") as devnull:
        with redirect_stderr(devnull):
            with YoutubeDL(opts) as ydl:
                raw = ydl.extract_info(url, download=False) or {}

    data = {}

    if duration := raw.get("duration"):
        duration = datetime.timedelta(seconds=duration)
        data |= {"duration": str(duration)}

    if date := raw.get("upload_date"):
        date = datetime.datetime.strptime(date, "%Y%m%d").strftime("%Y-%m-%d")
        data |= {"upload_date": date}

    return {"meta": data}
