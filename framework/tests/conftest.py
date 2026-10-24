import math
import time
from types import SimpleNamespace

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import config
from config import ARTIFACTS_DIR, TIMEOUT
from utils.artifact_manager import create_artifact_layout
from utils.error_classifier import classify_exception, classify_report_text
from utils.evidence import collect_failure_evidence
from utils.logging_config import configure_logging, event_context, get_logger

DEFAULT_BROWSER = getattr(config, "BROWSER", "chrome")


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
    parser.addoption(
        "--observe-seconds",
        type=float,
        default=3.0,
        help="Số giây quan sát cuối test; không dùng để đồng bộ DOM",
    )


def pytest_configure(config):
    seconds = config.getoption("--observe-seconds")
    if not math.isfinite(seconds) or seconds < 0:
        raise pytest.UsageError("--observe-seconds phải hữu hạn và >= 0")
    layout = create_artifact_layout(ARTIFACTS_DIR)
    logger, log_path = configure_logging(layout.logs, layout.run_id)
    config.artifact_layout = layout
    logger.info(
        f"Log file: {log_path}",
        extra=event_context(action="pytest_session", result="START"),
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return
    log = get_logger()
    if not report.failed:
        log.info(
            "Test PASS",
            extra=event_context(tc_id=item.name, action="pytest_report", result="PASS"),
        )
        return

    error = call.excinfo.value if call.excinfo else None
    category = (
        classify_exception(error)
        if error is not None
        else classify_report_text(report.longreprtext)
    )
    # JUnit chỉ đọc user_properties của report teardown, mà report đó
    # được dựng từ item.user_properties -> phải thêm vào item.
    item.user_properties.append(("error_category", category))
    allure.dynamic.label("error_category", category)
    log.error(
        f"Pytest item thất bại; category={category}",
        extra=event_context(tc_id=item.name, action="pytest_report", result="FAIL"),
    )

    driver = getattr(item, "driver", None)
    if driver is not None:
        collect_failure_evidence(
            driver, item.config.artifact_layout, item.nodeid, category
        )


@pytest.fixture
def driver(request):
    name = request.config.getoption("--browser") or DEFAULT_BROWSER
    headless = request.config.getoption("--headless")

    if name == "chrome":
        options = ChromeOptions()
        options.page_load_strategy = "eager"
        options.add_argument("--headless=new" if headless else "--start-maximized")
        drv = webdriver.Chrome(options=options)
    elif name == "edge":
        options = EdgeOptions()
        options.add_argument("--headless=new" if headless else "--start-maximized")
        drv = webdriver.Edge(options=options)
    else:
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        drv = webdriver.Firefox(options=options)

    if headless or name == "firefox":
        drv.set_window_size(1920, 1080)

    request.node.driver = drv  # MỚI: để hook makereport lấy được driver
    try:
        drv.set_page_load_timeout(45)  # MỚI
        yield drv
    finally:
        time.sleep(request.config.getoption("--observe-seconds"))  # MỚI
        drv.quit()


def pytest_sessionfinish(session, exitstatus):
    cfg = session.config
    layout = getattr(cfg, "artifact_layout", None)
    if layout is None:
        return
    env = (
        f"Browser={cfg.getoption('--browser') or DEFAULT_BROWSER}\n"
        f"Headless={cfg.getoption('--headless')}\n"
        f"RunId={layout.run_id}\n"
    )
    (layout.allure_results / "environment.properties").write_text(env, encoding="utf-8")
    get_logger().info(
        f"Kết thúc pytest session; exitstatus={exitstatus}",
        extra=event_context(action="pytest_session", result="END"),
    )


@pytest.fixture
def context(driver):
    return SimpleNamespace(driver=driver, timeout=TIMEOUT)
