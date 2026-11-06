"""Practice Form Page Object. Element locators are read from the Excel repository."""
from __future__ import annotations

from config import TIMEOUT
from pages.base_page import BasePage


class ValidationPage(BasePage):
    PAGE_NAME = "form"

    def __init__(self, driver, website: str, url: str, timeout: float = TIMEOUT):
        super().__init__(driver, locator_sheet=website, timeout=timeout)
        self.URL = url
