import time
import datetime
import json
import logging

import requests
import bs4


def gather_meta(url):
    print("fetching meta data...")

    data = requests.get(url)
    html = bs4.BeautifulSoup(data.text, features="html.parser")
    title = html.title.text

    meta_data = {
        "url": url,
        "title": title,
        "date": datetime.datetime.utcnow().isoformat(),
        "timestamp": int(time.time()),
    }

    with open("meta.json", "w") as f:
        json.dump(meta_data, f, indent=4)
