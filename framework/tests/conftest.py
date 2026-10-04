import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import config

DEFAULT_BROWSER = getattr(
    config, "BROWSER", "chrome"
)  # thêm BROWSER = "chrome" vào config.py


def pytest_addoption(parser):
    parser.addoption(
        "--browser",
        choices=["chrome", "firefox", "edge"],
        default=None,
        help=f"Trình duyệt (mặc định: {DEFAULT_BROWSER})",
    )
    parser.addoption(
        "--headless", action="store_true", help="Chạy không giao diện (CI)"
    )


@pytest.fixture
def driver(request):
    name = request.config.getoption("--browser") or DEFAULT_BROWSER
    headless = request.config.getoption("--headless")

    if name == "chrome":
        options = ChromeOptions()
        options.add_argument("--headless=new" if headless else "--start-maximized")
        driver = webdriver.Chrome(options=options)
    elif name == "edge":
        options = EdgeOptions()
        options.add_argument("--headless=new" if headless else "--start-maximized")
        driver = webdriver.Edge(options=options)
    else:
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        driver = webdriver.Firefox(options=options)

    if headless or name == "firefox":
        driver.set_window_size(1920, 1080)  # headless không có "maximize"

    yield driver
    driver.quit()


@pytest.fixture
def context(driver):
    # target_resolver._get_driver chấp nhận context["driver"] hoặc context.driver
    return {"driver": driver}
