"""Practice Form Page Object. Element locators are read from the Excel repository."""

from __future__ import annotations

from config import TIMEOUT
from pages.base_page import BasePage


class ValidationPage(BasePage):
    PAGE_NAME = "form"
    DOM_CLICK_FALLBACKS = frozenset({("demoQA", "submit")})

    def __init__(self, driver, website: str, url: str, timeout: int = TIMEOUT) -> None:
        super().__init__(driver, locator_sheet=website, timeout=timeout)
        self.URL = url
