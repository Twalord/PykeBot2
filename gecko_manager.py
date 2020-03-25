from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.service import WebDriverException


def open_session(headless=True):
    """
    Open a selenium web session in Firefox
    :return: webdriver, with an open session
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
            driver = webdriver.Firefox(executable_path=r'D:\Jonathan Decker\PycharmProjects\PykeBotRework\geckodriver'
                                                       r'.exe', options=options)
        else:
            driver = webdriver.Firefox(executable_path=r'D:\Jonathan Decker\PycharmProjects\PykeBotRework\geckodriver'
                                                       r'.exe')
        driver.implicitly_wait(10)

    return driver


def quit_session(driver: webdriver):
    driver.quit()
