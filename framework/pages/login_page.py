from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import LOGIN_URL, TIMEOUT


class LoginPage:

    LOCATORS = {
        "login.username": (By.ID, "userName"),
        "login.password": (By.ID, "password"),
        "login.loginButton": (By.CSS_SELECTOR, "button[type='submit']"),
        "login.userNameLabel": (By.ID, "userName-value"),
        "login.errorMessage": (By.CSS_SELECTOR, "#flash.error"),
    }

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, TIMEOUT)

    def open(self):
        self.driver.get(LOGIN_URL["login"])
