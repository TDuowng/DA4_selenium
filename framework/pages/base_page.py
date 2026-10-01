# pages/base_page.py
# BasePage class that serves as a base for all page objects

from pathlib import Path

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.locator_reader import get_locator_reader

LOCATOR_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "excel" / "locators.xlsx"
)


class BasePage:
    PAGE_NAME = ""

    # Initialize the BasePage and wait for the page to load
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.locators = get_locator_reader(str(LOCATOR_FILE))

    # Get locator
    def locator(self, element: str) -> tuple[str, str]:
        return self.locators.get_locator(self.PAGE_NAME, element)

    # --- Common actions ---
    # Find an element on the page using a locator after waiting for it to be visible
    def find_element(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    # Click an element on the page using a locator after waiting for it to be clickable
    def click_element(self, locator):
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    # Enter text into an input field on the page after clearing it first
    def enter_text(self, locator, text):
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    # Get the text of an element on the page using a locator
    def get_text(self, locator):
        return self.find_element(locator).text

    # Get the title of the current page
    def get_title(self):
        return self.driver.title

    # Get the current URL of the page
    def get_current_url(self):
        return self.driver.current_url
