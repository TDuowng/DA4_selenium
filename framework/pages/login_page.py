from config import DEFAULT_PASSWORD, DEFAULT_USERNAME, TIMEOUT
from pages.base_page import BasePage


class LoginPage(BasePage):
    PAGE_NAME = "login"

    def __init__(self, driver, website, url, timeout=TIMEOUT):
        super().__init__(driver, locator_sheet=website, timeout=timeout)

        self.website = website
        self.URL = url

    def login(self, username=None, password=None):
        self.open()

        self.enter_text(
            "username", username if username is not None else DEFAULT_USERNAME
        )

        self.enter_text(
            "password", password if password is not None else DEFAULT_PASSWORD
        )

        self.click("loginButton")
