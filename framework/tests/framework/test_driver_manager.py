from unittest.mock import Mock

import pytest

from config import PAGE_LOAD_TIMEOUT
from drivers import driver_manager


@pytest.mark.parametrize("browser", ["chrome", "edge", "firefox"])
@pytest.mark.parametrize("headless", [False, True])
def test_driver_manager_applies_shared_browser_settings(
    monkeypatch, browser, headless
):
    browser_driver = Mock()
    create_driver = Mock(return_value=browser_driver)
    monkeypatch.setattr(driver_manager.webdriver, browser.title(), create_driver)

    manager = driver_manager.DriverManager(browser=browser, headless=headless)
    assert manager.start_driver() is browser_driver

    options = create_driver.call_args.kwargs["options"]
    browser_driver.set_page_load_timeout.assert_called_once_with(PAGE_LOAD_TIMEOUT)
    if headless or browser == "firefox":
        browser_driver.set_window_size.assert_called_once_with(1920, 1080)
    else:
        browser_driver.maximize_window.assert_called_once_with()
    if browser == "chrome":
        assert options.page_load_strategy == "eager"
    if headless:
        assert any("headless" in option for option in options.arguments)

    manager.quit_driver()
    browser_driver.quit.assert_called_once_with()
    assert manager.driver is None


def test_driver_manager_closes_driver_when_setup_fails(monkeypatch):
    browser_driver = Mock()
    browser_driver.set_page_load_timeout.side_effect = RuntimeError("setup failed")
    monkeypatch.setattr(
        driver_manager.webdriver, "Chrome", Mock(return_value=browser_driver)
    )

    manager = driver_manager.DriverManager()
    with pytest.raises(RuntimeError, match="setup failed"):
        manager.start_driver()

    browser_driver.quit.assert_called_once_with()
    assert manager.driver is None
