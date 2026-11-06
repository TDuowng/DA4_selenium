from selenium.webdriver.support import expected_conditions as EC

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

        if self.website == "spcart":
            if not username or not password:
                raise ValueError("spcart cần username và password để đăng nhập admin")
            self.click("openLogin")
            self.enter_text("username", username)
            self.enter_text("password", password)
            self.click("loginButton")
            self.wait.until(
                EC.visibility_of_element_located(self.locator("loggedInIndicator"))
            )
            self.wait.until(
                EC.visibility_of_element_located(self.locator("adminPanel"))
            )
            return

        self.enter_text(
            "username", username if username is not None else DEFAULT_USERNAME
        )

        self.enter_text(
            "password", password if password is not None else DEFAULT_PASSWORD
        )

        self.click("loginButton")
