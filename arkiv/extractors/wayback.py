import time
from datetime import datetime
import json
import logging
from urllib.parse import urlparse


import waybackpy
from waybackpy.exceptions import WaybackError
import requests
import bs4

from ..config import USER_AGENT
from ..utils import shell, profile

log = logging.getLogger(__name__)


def _get_wayback_record(url, limit: int = 1):
    link = urlparse(url)
    log.debug(f"{link=}")

    scheme = f"{link.scheme}://" if link.scheme else ""

    query = "http://web.archive.org/cdx/search/cdx?url="
    params = f"&fl=timestamp&output=json&limit={limit}"
    wayback_url = f"{query}{scheme}{link.netloc}{link.path}{params}"
    log.debug(f"{wayback_url=}")

    cmd = ["curl", "-s", wayback_url]
    return_code, stdout, stderr = shell(cmd)

    if return_code:
        log.warning("failed to get timestamp from archive.org, skipping...")
        return None

    record = stdout.replace("\n", "").strip()
    log.debug(f"{record=}")

    data = json.loads(record)
    timestamp = data[1][0] if data else False

    if timestamp:
        return datetime.strptime(timestamp, "%Y%m%d%H%M%S").isoformat()


def _get_oldest_wayback_timestamp(url):
    return _get_wayback_record(url, 1)


def _get_newest_wayback_timestamp(url):
    return _get_wayback_record(url, -1)


@profile
def extract(url):
    log.info("extracting wayback data...")

    try:
        wayback = waybackpy.Url(url, USER_AGENT)
        oldest = wayback.oldest().timestamp.isoformat()
        newest = wayback.newest().timestamp.isoformat()
    except WaybackError:
        oldest = _get_oldest_wayback_timestamp(url)
        newest = _get_newest_wayback_timestamp(url)

    data = {}

    if oldest:
        data |= {"oldest-wayback-archive": oldest}

    if newest:
        data |= {"newest-wayback-archive": newest}

    return {"meta": data}
