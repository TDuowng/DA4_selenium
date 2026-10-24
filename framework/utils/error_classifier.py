from selenium.common.exceptions import (
    InvalidSelectorException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)


def classify_exception(error):
    names = {cls.__name__ for cls in type(error).__mro__}
    if "VerificationFailed" in names or isinstance(error, AssertionError):
        return "ASSERTION_FAILED"
    if isinstance(error, TimeoutException):
        return "TIMEOUT"
    if isinstance(error, NoSuchElementException):
        return "ELEMENT_NOT_FOUND"
    if isinstance(error, StaleElementReferenceException):
        return "STALE_ELEMENT"
    if isinstance(error, InvalidSelectorException):
        return "INVALID_SELECTOR"
    if isinstance(error, WebDriverException):
        return "WEBDRIVER_ERROR"
    if names & {"KeywordError", "TargetError"} or isinstance(
        error, (ValueError, KeyError, TypeError)
    ):
        return "DATA_OR_CONTRACT_ERROR"
    return "UNEXPECTED_ERROR"


def classify_report_text(text):
    """Phân loại dự phòng tại pytest hook khi chỉ còn traceback dạng chuỗi."""
    content = text or ""
    # Thứ tự quan trọng: VerificationFailed kế thừa KeywordError,
    # nên phải đứng trước KeywordError.
    patterns = (
        ("VerificationFailed", "ASSERTION_FAILED"),
        ("TimeoutException", "TIMEOUT"),
        ("NoSuchElementException", "ELEMENT_NOT_FOUND"),
        ("StaleElementReferenceException", "STALE_ELEMENT"),
        ("InvalidSelectorException", "INVALID_SELECTOR"),
        ("AssertionError", "ASSERTION_FAILED"),
        ("KeywordError", "DATA_OR_CONTRACT_ERROR"),
        ("TargetError", "DATA_OR_CONTRACT_ERROR"),
        ("ValueError", "DATA_OR_CONTRACT_ERROR"),
    )
    for token, category in patterns:
        if token in content:
            return category
    return "UNEXPECTED_ERROR"
