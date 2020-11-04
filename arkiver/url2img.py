import os
import logging

from selenium import webdriver


log = logging.getLogger(__name__)


def generate_screenshots(url):
    options = webdriver.FirefoxOptions()
    options.set_headless()

    profile = webdriver.FirefoxProfile()
    profile.set_preference("javascript.enabled", False)
    profile.set_preference("network.cookie.cookieBehavior", 2)

    driver = webdriver.Firefox(
        firefox_profile=profile, firefox_options=options, log_path=os.devnull
    )

    driver.get(url)

    log.info("generating thumbnail...")
    driver.save_screenshot("thumbnail.png")

    log.info("generating full-page image...")
    body = driver.find_element_by_tag_name("body")
    body.screenshot("fullpage.png")

    driver.delete_all_cookies()
    driver.quit()
