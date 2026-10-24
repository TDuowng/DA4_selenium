# ============================================================
# KIỂM TRA PHÂN LOẠI LỖI
# Cùng một vocabulary lỗi cho log, JUnit và Allure.
# Không mở browser.
# ============================================================
import pytest
from selenium.common.exceptions import (
    InvalidSelectorException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)

from utils.error_classifier import classify_exception, classify_report_text

pytestmark = pytest.mark.framework


# classify_exception so sánh theo TÊN class (qua MRO), nên dựng class giả
# cùng tên để test không phụ thuộc việc import package keywords.
class KeywordError(Exception):
    pass


class VerificationFailed(KeywordError):
    pass


class TargetError(Exception):
    pass


@pytest.mark.parametrize(
    ("error", "expected"),
    [
        (AssertionError("actual != expected"), "ASSERTION_FAILED"),
        (VerificationFailed("VerifyText: Expected='a'"), "ASSERTION_FAILED"),
        (TimeoutException("10 seconds"), "TIMEOUT"),
        (NoSuchElementException("#missing"), "ELEMENT_NOT_FOUND"),
        (StaleElementReferenceException("old DOM"), "STALE_ELEMENT"),
        (InvalidSelectorException("//["), "INVALID_SELECTOR"),
        (WebDriverException("session closed"), "WEBDRIVER_ERROR"),
        (KeywordError("Target không được để trống"), "DATA_OR_CONTRACT_ERROR"),
        (TargetError("Không tìm thấy Page Object"), "DATA_OR_CONTRACT_ERROR"),
        (ValueError("missing column"), "DATA_OR_CONTRACT_ERROR"),
        (RuntimeError("unexpected"), "UNEXPECTED_ERROR"),
    ],
)
def test_classify_exception(error, expected):
    assert classify_exception(error) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("keywords.keyword_utils.VerificationFailed: VerifyUrl", "ASSERTION_FAILED"),
        ("selenium.common.exceptions.TimeoutException", "TIMEOUT"),
        ("keywords.keyword_utils.KeywordError: Navigate", "DATA_OR_CONTRACT_ERROR"),
        ("", "UNEXPECTED_ERROR"),
        (None, "UNEXPECTED_ERROR"),
    ],
)
def test_classify_report_text(text, expected):
    assert classify_report_text(text) == expected
