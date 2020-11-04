import time
import datetime
import json
import logging

import requests
import bs4

from shell_utils import shell

log = logging.getLogger(__name__)


def _get_first_webarchive_record(url):
    query = "http://web.archive.org/cdx/search/cdx?url="
    params = "&fl=timestamp&output=json&limit=1"
    url = f"{query}{url}{params}"

    cmd = ["curl", "-s", url]
    return_code, stdout, stderr = shell(cmd, log=False)

    if return_code:
        log.warning(f"failed to get first occurance from webarchive, skipping...")
        return "unknown"

    record = stdout.replace("\n", " ").strip()
    log.debug(f"{stdout=}")

    j = json.loads(record)
    timestamp = j[1][0] if j else False
    date = datetime.datetime.strptime(timestamp, "%Y%m%d%H%M%S").isoformat() if timestamp else ""
    return date


def gather_meta(url):
    log.info("fetching meta data...")

    data = requests.get(url)
    html = bs4.BeautifulSoup(data.text, features="html.parser")
    title = html.title.text.strip()
    first = _get_first_webarchive_record(url)

    meta_data = {
        "url": url,
        "title": title,
        "date": datetime.datetime.utcnow().isoformat(),
        "first-occurance": first,
    }

    with open("meta.json", "w") as f:
        json.dump(meta_data, f, indent=4)