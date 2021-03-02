from datetime import datetime
import logging

import requests
import bs4

from ..utils import profile

log = logging.getLogger(__name__)


@profile
def extract(url):
    log.info("extracting meta data...")

    data = requests.get(url)
    html = bs4.BeautifulSoup(data.text, features="html.parser")
    title = html.title.text.strip()

    meta_data = {
        "url": url,
        "title": title,
        "timestamp": datetime.utcnow().isoformat(),
    }

    return {"meta": meta_data}
