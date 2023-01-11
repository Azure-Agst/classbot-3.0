from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from .env import env

def get_wait(driver: webdriver):
    """Returns a WebDriverWait object"""

    return WebDriverWait(driver, env.timeout)

def check_xpath_exists(driver: webdriver, xpath: str):
    """Checks to see if item at given xpath exists"""

    # Simple try-catch :)
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True

def check_id_exists(driver: webdriver, id: str):
    """Checks to see if item at given id exists"""

    # Simple try-catch :)
    try:
        driver.find_element(By.ID, id)
    except NoSuchElementException:
        return False
    return True