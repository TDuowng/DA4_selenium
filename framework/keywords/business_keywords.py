# keywords/login_keywords.py
from __future__ import annotations

from typing import Any

from .keyword_utils import (
    KeywordError,
    KeywordResult,
    require_target,
)
from .target_resolver import TargetError, resolve_target

from pages.base_page import BasePage


def _run_page_action(
    page: BasePage, action_name: str, keyword_name: str, *args: Any
) -> None:
    action = getattr(page, action_name, None)
    if not callable(action):
        raise KeywordError(
            f"{keyword_name}: {type(page).__name__} "
            f"chưa triển khai {action_name}()."
        )
    action(*args)


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
        Optional username/password pair. Blank uses configured defaults.

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

    if data is None or data == "":
        _run_page_action(page, "login", "Login")
    else:
        if not isinstance(data, str) or "/" not in data:
            raise KeywordError("Login: Data phải có dạng username/password.")
        username, password = data.split("/", 1)
        if not username or not password:
            raise KeywordError("Login: username và password không được để trống.")
        _run_page_action(page, "login", "Login", username, password)

    return KeywordResult.ok(f"Login executed on {target_name}")


def add_to_cart(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: AddToCart

    Target: ProductPage.
    Data: product name|quantity, for example Fresh Carrots|2.

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

    if not isinstance(data, str) or "|" not in data:
        raise KeywordError("AddToCart: Data phải có dạng product name|quantity.")
    product_name, quantity_text = data.rsplit("|", 1)
    try:
        quantity = int(quantity_text)
    except ValueError as exc:
        raise KeywordError("AddToCart: quantity phải là số nguyên dương.") from exc
    if not product_name.strip() or quantity < 1:
        raise KeywordError("AddToCart: cần tên sản phẩm và quantity > 0.")

    _run_page_action(page, "add_to_cart", "AddToCart", product_name.strip(), quantity)

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

    _run_page_action(page, "set_product_out_of_stock", "SetProductOutOfStock")

    return KeywordResult.ok(f"Product set out of stock using {target_name}")
