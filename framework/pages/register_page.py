from config import TIMEOUT
from pages.base_page import BasePage


class RegisterPage(BasePage):
    PAGE_NAME = "register"
    DOM_CLICK_FALLBACKS = frozenset({("taophoBA", "registerButton")})

    def __init__(self, driver, website, url, timeout=TIMEOUT):
        super().__init__(driver, locator_sheet=website, timeout=timeout)
        self.website = website
        self.URL = url
