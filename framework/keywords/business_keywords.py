# keywords/login_keywords.py
from __future__ import annotations

from typing import Any

from .keyword_utils import (
    KeywordError,
    KeywordResult,
    require_target,
)
from .target_resolver import TargetError, resolve_target

from pages.login_page import LoginPage


def __init__(self, driver):
    self.page = LoginPage(driver)


def verify_login_error(self, target, data, expected):
    actual = self.page.get_error()
    assert actual == expected, f"Login error: expected={expected!r}, actual={actual!r}"


def verify_login_success(self, target, data, expected):
    assert "dashboard" in self.driver.current_url


##______________________________________________________________________


def login(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: Login

    Target:
        LoginPage.

    Data:
        Not used.

    Expected:
        Not used.
    """
    target_name = require_target("Login", target)

    try:
        page, element_key = resolve_target(target_name, context)
    except (TargetError, KeyError) as exc:
        raise KeywordError(f"Login: {exc}") from exc

    if element_key is not None:
        raise KeywordError(f"Login chỉ nhận Target là Page: '{target_name}'")

    page.login()

    return KeywordResult.ok(f"Login executed on {target_name}")


def add_to_cart(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: AddToCart

    Target:
        ProductPage.

    Data:
        Not used.

    Expected:
        Not used.
    """
    target_name = require_target("AddToCart", target)

    try:
        page, element_key = resolve_target(target_name, context)
    except (TargetError, KeyError) as exc:
        raise KeywordError(f"AddToCart: {exc}") from exc

    if element_key is not None:
        raise KeywordError(f"AddToCart chỉ nhận Target là Page: '{target_name}'")

    page.add_to_cart()

    return KeywordResult.ok(f"Added product to cart using {target_name}")


def set_product_out_of_stock(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: SetProductOutOfStock

    Target:
        ProductPage.

    Data:
        Not used.

    Expected:
        Not used.
    """
    target_name = require_target(
        "SetProductOutOfStock",
        target,
    )

    try:
        page, element_key = resolve_target(target_name, context)
    except (TargetError, KeyError) as exc:
        raise KeywordError(f"SetProductOutOfStock: {exc}") from exc

    if element_key is not None:
        raise KeywordError(
            "SetProductOutOfStock chỉ nhận Target là Page: " f"'{target_name}'"
        )

    page.set_product_out_of_stock()

    return KeywordResult.ok(f"Product set out of stock using {target_name}")
