"""Trang tìm kiếm, dùng locator và URL riêng của từng website."""

from config import TIMEOUT
from pages.base_page import BasePage


class SearchPage(BasePage):
    PAGE_NAME = "search"

    def __init__(self, driver, website, url, timeout=TIMEOUT):
        if not website:
            raise ValueError("SearchPage cần website từ test case")

        if not url:
            raise ValueError("SearchPage cần URL từ sheet sites của Excel")

        super().__init__(
            driver,
            locator_sheet=website,
            timeout=timeout,
        )

        self.website = website
        self.URL = url
