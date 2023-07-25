"""
Offers utility to open a firefox webdriver.
Uses webdriver-manager to acquire Geckodriver.

:author: Jonathan Decker
"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.webdriver import WebDriver
from webdriver_manager.firefox import GeckoDriverManager


def open_session(headless=True) -> WebDriver:
    """
    :description: Opens a Selenium Firefox web session.
    Uses webdriver-manager to acquire Geckodriver.
    :param headless: Set whether the web session should be headless or not.
    :type headless: bool
    :return: A new firefox webdriver.
    :rtype: selenium.webdriver
    """
    options = Options()
    options.add_argument("--headless=new")

    service = FirefoxService(GeckoDriverManager().install())

    # opens a web session and returns the webdriver
    if headless:
        driver = webdriver.Firefox(options=options, service=service)
    else:
        driver = webdriver.Firefox(service=service)
    driver.implicitly_wait(30)

    return driver


def quit_session(driver: webdriver):
    driver.quit()
