"""Cart page elements used by the passing empty-cart cases."""

from config import TIMEOUT
from pages.base_page import BasePage


class CartPage(BasePage):
    PAGE_NAME = "cart"

    def __init__(self, driver, website, url, timeout=TIMEOUT):
        super().__init__(driver, locator_sheet=website, timeout=timeout)
        self.website = website
        self.URL = url
