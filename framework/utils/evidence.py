# BẰNG CHỨNG KHI FAIL: screenshot + page source + URL -> lưu file và đính kèm Allure.
import allure

from utils.artifact_manager import safe_artifact_name
from utils.logging_config import event_context, get_logger


def collect_failure_evidence(driver, layout, node_name, category):
    log = get_logger()
    name = safe_artifact_name(node_name)
    saved = {}

    def attempt(label, action):
        # Browser có thể đã chết: một bằng chứng lỗi không được che mất lỗi gốc.
        try:
            action()
        except Exception as exc:
            log.warning(
                f"Không lấy được {label}: {exc}",
                extra=event_context(action="evidence", result="SKIP"),
            )

    def screenshot():
        path = layout.screenshots / f"{name}.png"
        driver.save_screenshot(str(path))
        saved["screenshot"] = path
        allure.attach.file(str(path), "screenshot", allure.attachment_type.PNG)

    def page_source():
        path = layout.page_sources / f"{name}.html"
        path.write_text(driver.page_source, encoding="utf-8")
        saved["page_source"] = path
        allure.attach.file(str(path), "page_source", allure.attachment_type.HTML)

    def url():
        saved["url"] = driver.current_url
        allure.attach(driver.current_url, "current_url", allure.attachment_type.TEXT)

    attempt("screenshot", screenshot)
    attempt("page source", page_source)
    attempt("URL", url)

    log.error(
        f"Bằng chứng: {saved}",
        extra=event_context(
            node_name, "-", "evidence", saved.get("url", "-"), category
        ),
    )
    return saved
