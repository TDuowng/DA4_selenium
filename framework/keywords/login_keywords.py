# keywords/login_keywords.py
from pages.login_page import LoginPage

class LoginKeywords:
    def __init__(self, driver):
        self.page = LoginPage(driver)

    def verify_login_error(self, target, data, expected):
        actual = self.page.get_error()
        assert actual == expected, f"Login error: expected={expected!r}, actual={actual!r}"

    def verify_login_success(self, target, data, expected):
        assert "dashboard" in self.driver.current_url