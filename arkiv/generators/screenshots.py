import os
import logging

from selenium import webdriver

from ..utils import profile

log = logging.getLogger(__name__)


@profile
def generate(url):
    log.info("generating screenshots...")

    options = webdriver.FirefoxOptions()
    options.set_headless()

    profile = webdriver.FirefoxProfile()
    profile.set_preference("javascript.enabled", False)
    profile.set_preference("network.cookie.cookieBehavior", 2)

    with webdriver.Firefox(
        firefox_profile=profile, firefox_options=options, log_path=os.devnull
    ) as driver:
        driver.get(url)

        log.info("- generating thumbnail...")
        driver.save_screenshot("thumbnail.png")

        log.info("- generating page image...")
        width = driver.execute_script("return document.body.parentNode.scrollWidth")
        height = driver.execute_script("return document.body.parentNode.scrollHeight")
        # the UI obscures a part of the viewport, need to account for that
        driver.set_window_size(width, height + 100)
        log.debug(f"full page size: {width}x{height}")

        html = driver.find_element_by_tag_name("html")
        html.screenshot("page.png")

        driver.delete_all_cookies()
