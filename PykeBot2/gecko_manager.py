"""
Offers utility to open a firefox webdriver.
Geckodriver should be in PATH for this.

:author: Jonathan Decker
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.service import WebDriverException
from selenium.webdriver.firefox.webdriver import WebDriver


def open_session(headless=True) -> WebDriver:
    """
    :description: Opens a Selenium Firefox web session.
    Attempts to find geckodriver from PATH, if it fails uses a static path.
    :param headless: Set whether the web session should be headless or not.
    :type headless: bool
    :return: A new firefox webdriver.
    :rtype: selenium.webdriver
    """
    options = Options()
    options.add_argument("--headless")

    # opens a web session and returns the webdriver
    try:
        if headless:
            driver = webdriver.Firefox(options=options)
        else:
            driver = webdriver.Firefox()
        driver.implicitly_wait(30)
    except WebDriverException:
        if headless:
            driver = webdriver.Firefox(
                executable_path=r"/geckodriver.exe", options=options
            )
        else:
            driver = webdriver.Firefox(executable_path=r"/geckodriver.exe")
        driver.implicitly_wait(10)

    return driver


def quit_session(driver: webdriver):
    driver.quit()
