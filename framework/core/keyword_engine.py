from framework.keywords.keyword_registry import build_default_registry
from selenium.common.exceptions import TimeoutException


class KeywordEngine:
    """Chỉ THỰC THI các bước đã validate + bind. Không đọc Excel, không thay placeholder."""

    def __init__(self, driver, registry=None):
        self.driver = driver
        self.registry = registry or build_default_registry()

    def run(self, steps):
        for s in steps:
            handler = self.registry.resolve(s["keyword"])
            try:
                handler(
                    self.driver, s["target"], s["data"], s["expected"]
                )  # thứ tự tham số: GIẢ ĐỊNH
            except (AssertionError, TimeoutException) as e:
                raise AssertionError(
                    f"[{s['case_id']}] step {s['step']} ({s['keyword']}) lỗi: {e}"
                ) from None
