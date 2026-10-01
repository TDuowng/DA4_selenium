# keywords/common_keywords.py

from __future__ import annotations

from typing import Any

from .keyword_utils import (
    KeywordError,
    KeywordResult,
    require_data,
    require_target,
)

from .target_resolver import (
    TargetError,
    resolve_target,
)


def navigate(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: Navigate
    Target:
        Page Object name.
    Data:
        Not used.
    Expected:
        Not used.
    Example:
        Navigate | LoginPage
    """

    target_name = require_target(
        "Navigate",
        target,
    )

    try:
        page, element_key = resolve_target(
            target_name,
            context,
        )

    except (TargetError, KeyError) as exc:
        raise KeywordError(f"Navigate: {exc}") from exc

    if element_key is not None:
        raise KeywordError(
            f"Navigate chỉ nhận Target là tên Page, "
            f"không phải element: '{target_name}'"
        )

    page.open()

    return KeywordResult.ok(f"Navigated to {target_name}")


def set_text(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: SetText
    Target:
        PageObject.Element
    Data:
        Text to input.
    Expected:
        Not used.
    Example:
        SetText | LoginPage.Username | admin
    """

    target_name = require_target(
        "SetText",
        target,
    )

    value = require_data(
        "SetText",
        data,
    )

    try:
        page, element_key = resolve_target(
            target_name,
            context,
        )

    except (TargetError, KeyError) as exc:
        raise KeywordError(f"SetText: {exc}") from exc

    if element_key is None:
        raise KeywordError(f"SetText yêu cầu Target là element: " f"'{target_name}'")

    if value == "<empty>":
        page.clear(element_key)
    else:
        page.enter_text(
            element_key,
            value,
        )

    return KeywordResult.ok(f"Set text for {target_name}")


def clear_text(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: ClearText
    Target:
        PageObject.Element
    Data:
        Not used.
    Expected:
        Not used.
    """

    target_name = require_target(
        "ClearText",
        target,
    )

    try:
        page, element_key = resolve_target(
            target_name,
            context,
        )
    except (TargetError, KeyError) as exc:
        raise KeywordError(f"ClearText: {exc}") from exc

    if element_key is None:
        raise KeywordError(f"ClearText yêu cầu Target là element: " f"'{target_name}'")

    page.clear(element_key)

    return KeywordResult.ok(f"Cleared text from {target_name}")


def click_element(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: ClickElement
    Target:
        PageObject.Element
    Data:
        Not used.
    Expected:
        Not used.
    """

    target_name = require_target(
        "ClickElement",
        target,
    )

    try:
        page, element_key = resolve_target(
            target_name,
            context,
        )

    except (TargetError, KeyError) as exc:
        raise KeywordError(f"ClickElement: {exc}") from exc

    if element_key is None:
        raise KeywordError(
            f"ClickElement yêu cầu Target là element: " f"'{target_name}'"
        )

    page.click(element_key)

    return KeywordResult.ok(f"Clicked {target_name}")


def click_outside(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: ClickOutside
    Target:
        PageObject.
    Data:
        Not used.
    Expected:
        Not used.
    """

    target_name = require_target(
        "ClickOutside",
        target,
    )

    try:
        page, element_key = resolve_target(
            target_name,
            context,
        )
    except (TargetError, KeyError) as exc:
        raise KeywordError(f"ClickOutside: {exc}") from exc

    if element_key is not None:
        raise KeywordError(f"ClickOutside chỉ nhận Target là Page: " f"'{target_name}'")

    page.click_outside()

    return KeywordResult.ok(f"Clicked outside on {target_name}")


def select_option(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: SelectOption
    Target:
        PageObject.Element
    Data:
        Option value/text.
    Expected:
        Not used.
    """

    target_name = require_target(
        "SelectOption",
        target,
    )

    option = require_data(
        "SelectOption",
        data,
    )

    try:
        page, element_key = resolve_target(
            target_name,
            context,
        )

    except (TargetError, KeyError) as exc:
        raise KeywordError(f"SelectOption: {exc}") from exc

    if element_key is None:
        raise KeywordError(
            f"SelectOption yêu cầu Target là element: " f"'{target_name}'"
        )

    page.select_option(
        element_key,
        option,
    )

    return KeywordResult.ok(f"Selected '{option}' from {target_name}")
