import os
import logging

from selenium import webdriver


log = logging.getLogger(__name__)


def generate(url):
    options = webdriver.FirefoxOptions()
    options.set_headless()

    profile = webdriver.FirefoxProfile()
    profile.set_preference("javascript.enabled", False)
    profile.set_preference("network.cookie.cookieBehavior", 2)

    with webdriver.Firefox(
        firefox_profile=profile, firefox_options=options, log_path=os.devnull
    ) as driver:
        driver.get(url)

        log.info("generating thumbnail...")
        driver.save_screenshot("thumb.png")

        log.info("generating <html> image...")
        html = driver.find_element_by_tag_name("html")
        html.screenshot("html.png")

        log.info("generating <body> image...")
        body = driver.find_element_by_tag_name("body")
        body.screenshot("body.png")

        driver.delete_all_cookies()
