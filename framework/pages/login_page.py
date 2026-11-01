from config import DEFAULT_PASSWORD, DEFAULT_USERNAME, SITE_CONFIG
from pages.base_page import BasePage


class LoginPage(BasePage):
    PAGE_NAME = "login"

    def __init__(self, driver, website="demoQA"):
        if website not in SITE_CONFIG:
            raise ValueError(f"Website không hỗ trợ: {website}")

        site = SITE_CONFIG[website]

        super().__init__(driver, locator_sheet=site["locator_sheet"])

        self.website = website
        self.URL = site["url"]

    def login(self, username=None, password=None):
        self.open()

        self.enter_text(
            "username", username if username is not None else DEFAULT_USERNAME
        )

        self.enter_text(
            "password", password if password is not None else DEFAULT_PASSWORD
        )

        self.click("loginButton")
