# DRIVER MANAGER: quản lý vòng đời WebDriver (Chrome/Firefox/Edge, headless tuỳ chọn).
# Không phụ thuộc pytest -> tái sử dụng được ở bất kỳ đâu.

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from config import PAGE_LOAD_TIMEOUT

SUPPORTED_BROWSERS = {"chrome", "firefox", "edge"}


class DriverManager:
    def __init__(
        self,
        browser: str = "chrome",
        headless: bool = False,
        page_load_timeout: float = PAGE_LOAD_TIMEOUT,
    ):
        browser = browser.lower()
        if browser not in SUPPORTED_BROWSERS:
            raise ValueError(
                f"Browser không hỗ trợ: {browser}. "
                f"Chỉ chấp nhận: {sorted(SUPPORTED_BROWSERS)}"
            )
        self.browser = browser
        self.headless = headless
        self.page_load_timeout = page_load_timeout
        self.driver = None

    def start_driver(self):
        """Khởi tạo driver theo self.browser, lưu và trả về instance."""
        starters = {
            "chrome": self._start_chrome,
            "firefox": self._start_firefox,
            "edge": self._start_edge,
        }
        self.driver = starters[self.browser]()
        try:
            self.driver.set_page_load_timeout(self.page_load_timeout)
            if self.headless or self.browser == "firefox":
                self.driver.set_window_size(1920, 1080)
            else:
                self.driver.maximize_window()
        except Exception:
            self.quit_driver()
            raise
        return self.driver

    def _start_chrome(self):
        options = ChromeOptions()
        options.page_load_strategy = "eager"
        options.add_argument("--headless=new" if self.headless else "--start-maximized")
        return webdriver.Chrome(options=options)

    def _start_firefox(self):
        options = FirefoxOptions()
        if self.headless:
            options.add_argument("-headless")
        return webdriver.Firefox(options=options)

    def _start_edge(self):
        options = EdgeOptions()
        options.add_argument("--headless=new" if self.headless else "--start-maximized")
        return webdriver.Edge(options=options)

    def get_driver(self):
        """Trả về driver hiện tại. Raise lỗi nếu chưa start_driver()."""
        if self.driver is None:
            raise RuntimeError("Driver chưa được khởi tạo. Gọi start_driver() trước.")
        return self.driver

    def quit_driver(self):
        """Đóng browser, an toàn khi gọi nhiều lần hoặc chưa từng start."""
        if self.driver is not None:
            self.driver.quit()
            self.driver = None


# Chạy thử độc lập, không cần pytest:
# python drivers/driver_manager.py --browser firefox --headless
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", default="chrome", choices=sorted(SUPPORTED_BROWSERS))
    parser.add_argument("--headless", action="store_true")
    args = parser.parse_args()

    manager = DriverManager(browser=args.browser, headless=args.headless)
    driver = manager.start_driver()
    driver.get("https://example.com")
    print("Browser:", args.browser, "| Title:", driver.title)
    manager.quit_driver()
