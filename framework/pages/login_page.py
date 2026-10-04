from selenium.webdriver.common.by import By

# pages/login_page.py
from config import DEFAULT_PASSWORD, DEFAULT_USERNAME, LOGIN_URL
from pages.base_page import BasePage


class LoginPage(BasePage):
    PAGE_NAME = "login"  # khớp cột Page trong locators.xlsx
    URL = LOGIN_URL["login"]

    def login(self, username: str | None = None, password: str | None = None):
        self.open()
        self.enter_text(
            "username", username if username is not None else DEFAULT_USERNAME
        )
        self.enter_text(
            "password", password if password is not None else DEFAULT_PASSWORD
        )
        self.click("loginButton")
