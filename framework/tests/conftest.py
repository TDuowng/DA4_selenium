import pytest
from drivers.driver_manager import DriverManager
 
 
def pytest_addoption(parser):
    """Cho phép chọn browser/headless khi chạy: pytest --browser=firefox --headless"""
    parser.addoption("--browser", action="store", default="chrome",
                      help="chrome | firefox | edge")
    parser.addoption("--headless", action="store_true", default=False,
                      help="Chạy browser ở chế độ headless")
 
 
@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser")
    headless = request.config.getoption("--headless")
 
    manager = DriverManager(browser=browser, headless=headless)
    drv = manager.start_driver()
 
    yield drv
 
    manager.quit_driver()