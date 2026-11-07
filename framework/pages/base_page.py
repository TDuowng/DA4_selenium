# pages/base_page.py
# BasePage class that serves as a base for all page objects

from pathlib import Path

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

from config import TIMEOUT
from utils.locator_reader import get_locator_reader

LOCATOR_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "excel" / "locators.xlsx"
)


class BasePage:
    PAGE_NAME = ""
    DOM_CLICK_FALLBACKS = frozenset()

    # Initialize the BasePage and wait for the page to load
    def __init__(self, driver, locator_sheet=None, timeout=TIMEOUT):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)
        self.locators = get_locator_reader(str(LOCATOR_FILE))
        self.locator_sheet = locator_sheet

    # Get locator
    def locator(self, element: str) -> tuple[str, str]:
        return self.locators.get_locator(
            self.PAGE_NAME, element, sheet=self.locator_sheet
        )

    # --- Common actions ---
    def _resolve_locator(self, element: str | tuple[str, str]) -> tuple[str, str]:
        return self.locator(element) if isinstance(element, str) else element

    # Find an element on the page using a locator after waiting for it to be visible
    def find_element(self, element: str | tuple[str, str]):
        locator = self._resolve_locator(element)
        return self.wait.until(EC.visibility_of_element_located(locator))

    # Click an element on the page using a locator after waiting for it to be clickable
    def click_element(self, locator):
        element = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});",
            element,
        )
        element.click()

    # Enter text into an input field on the page after clearing it first
    def enter_text(self, element: str | tuple[str, str], text: str):
        web_element = self.find_element(element)
        web_element.clear()
        web_element.send_keys(text)

    def open(self):
        url = getattr(self, "URL", None)
        if not url:
            raise ValueError(f"{type(self).__name__} must define URL")
        self.driver.get(url)

    def click(self, element: str):
        locator = self.locator(element)
        try:
            self.click_element(locator)
        except ElementClickInterceptedException:
            if (self.locator_sheet, element) not in self.DOM_CLICK_FALLBACKS:
                raise
            self.driver.execute_script(
                "arguments[0].click();", self.find_element(locator)
            )

    def clear(self, element: str):
        self.find_element(element).clear()

    def clear_with_keyboard(self, element_key):
        locator = self.locator(element_key)

        element = self.wait.until(EC.visibility_of_element_located(locator))

        # Focus vào input mà không click chuột
        self.driver.execute_script("arguments[0].focus();", element)

        # Xóa bằng bàn phím để kích hoạt sự kiện input
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)

    # Get the text of an element on the page using a locator
    def get_text(self, element: str | tuple[str, str]):
        return self.find_element(element).text

    def is_enabled(self, element: str) -> bool:
        return self.driver.find_element(*self.locator(element)).is_enabled()

    def is_selected(self, element: str) -> bool:
        return self.driver.find_element(*self.locator(element)).is_selected()

    def is_valid(self, element: str) -> bool:
        web_element = self.driver.find_element(*self.locator(element))
        return self.driver.execute_script(
            "return arguments[0].validity.valid;",
            web_element,
        )

    def is_visible(self, element: str) -> bool:
        try:
            return self.driver.find_element(*self.locator(element)).is_displayed()
        except NoSuchElementException:
            return False

    def is_present(self, element: str) -> bool:
        return bool(self.driver.find_elements(*self.locator(element)))

    def get_attribute(self, element: str, attribute: str):
        return self.driver.find_element(*self.locator(element)).get_attribute(attribute)

    def count_elements(self, element: str) -> int:
        return len(self.driver.find_elements(*self.locator(element)))

    def click_outside(self):
        self.driver.find_element(By.TAG_NAME, "body").click()

    def select_option(self, element: str, option: str):
        Select(self.find_element(element)).select_by_visible_text(option)

    # Get the title of the current page
    def get_title(self):
        return self.driver.title

    # Get the current URL of the page
    def get_current_url(self):
        return self.driver.current_url
