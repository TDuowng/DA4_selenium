"""Product catalog actions shared by cart tests."""

import re

from config import TIMEOUT
from pages.base_page import BasePage
from selenium.common.exceptions import TimeoutException


class ProductPage(BasePage):
    PAGE_NAME = "product"

    def __init__(self, driver, website, url, timeout=TIMEOUT):
        super().__init__(driver, locator_sheet=website, timeout=timeout)
        self.website = website
        self.URL = url

    def add_to_cart(self, product_name: str, quantity: int) -> None:
        for _ in range(quantity):
            try:
                card = self.wait.until(
                    lambda driver: next(
                        (
                            item
                            for item in driver.find_elements(*self.locator("cards"))
                            if item.find_element(*self.locator("name")).text.strip()
                            == product_name
                        ),
                        None,
                    ),
                    f"Không tìm thấy sản phẩm {product_name!r} trên {self.website}",
                )
            except TimeoutException as exc:
                raise ValueError(
                    f"Không tìm thấy sản phẩm {product_name!r} trên {self.website}"
                ) from exc
            if card is None:
                raise ValueError(
                    f"Không tìm thấy sản phẩm {product_name!r} trên {self.website}"
                )

            previous_count = self._cart_count()
            button = card.find_element(*self.locator("addButton"))
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", button
            )
            button.click()
            self.wait.until(
                lambda _: self._cart_count() > previous_count
            )

    def _cart_count(self) -> int:
        elements = self.driver.find_elements(*self.locator("cartCount"))
        if not elements:
            return 0
        label = elements[0].get_attribute("aria-label")
        if label:
            match = re.search(r"\b\d+\b", label)
            if match is None:
                raise ValueError(f"Không đọc được số lượng giỏ từ {label!r}")
            return int(match.group())
        return int(elements[0].text)
