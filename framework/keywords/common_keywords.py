# keywords/common_keywords.py
class CommonKeywords:
    def __init__(self, driver):
        self.driver = driver

    def navigate(self, target, data, expected):
        from config import URLS
        self.driver.get(URLS[data])

    def set_text(self, target, data, expected):
        # target dạng "login.username", "cart.quantity"...
        self.driver.find_element(*self._locator(target)).send_keys(data)

    def click_element(self, target, data, expected):
        self.driver.find_element(*self._locator(target)).click()