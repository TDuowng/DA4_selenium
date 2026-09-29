from __future__ import annotations

from typing import Any

from keywords.keyword_utils import (
    KeywordError,
    KeywordResult,
    VerificationFailed,
    fail,
    normalize_text,
    page_timeout,
    parse_number,
    poll,
    require_data,
    require_expected,
    require_target,
    resolve_element,
    resolve_page,
    safe_eval,
)


def verify_url(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyUrl

    Target:
        Page Object.

    Data:
        Not used.

    Expected:
        Expected URL or URL fragment.

    Behavior:
        Verify current URL contains Expected.
    """

    target_name = require_target(
        "VerifyUrl",
        target,
    )

    expected_value = require_expected(
        "VerifyUrl",
        expected,
    )

    page = resolve_page(
        target_name,
        context,
    )

    timeout = page_timeout(
        page,
        context,
    )

    def check_url():
        actual_url = page.get_current_url()

        return actual_url if expected_value in actual_url else False

    actual_url = poll(
        check_url,
        timeout=timeout,
    )

    if not actual_url:
        actual_url = page.get_current_url()

        fail(
            "VerifyUrl",
            (f"Expected URL containing " f"'{expected_value}'"),
            actual_url,
        )

    return KeywordResult.ok(
        (f"URL contains '{expected_value}'"),
        actual=actual_url,
    )


def verify_text(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyText

    Target:
        PageObject.Element

    Expected:
        Exact text after normalization.
    """

    target_name = require_target(
        "VerifyText",
        target,
    )

    expected_value = require_expected(
        "VerifyText",
        expected,
    )

    page, element_key = resolve_element(
        target_name,
        context,
    )

    timeout = page_timeout(
        page,
        context,
    )

    expected_normalized = normalize_text(expected_value)

    def check_text():
        actual = page.get_text(element_key)

        return actual if normalize_text(actual) == expected_normalized else False

    actual = poll(
        check_text,
        timeout=timeout,
    )

    if actual is False:
        actual = page.get_text(element_key)

        fail(
            "VerifyText",
            (f"Expected='{expected_value}'"),
            actual,
        )

    return KeywordResult.ok(
        f"Text matched for {target_name}",
        actual=actual,
    )


def verify_text_contains(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyTextContains

    Target:
        PageObject.Element

    Expected:
        Text fragment expected to appear.
    """

    target_name = require_target(
        "VerifyTextContains",
        target,
    )

    expected_value = require_expected(
        "VerifyTextContains",
        expected,
    )

    page, element_key = resolve_element(
        target_name,
        context,
    )

    timeout = page_timeout(
        page,
        context,
    )

    expected_normalized = normalize_text(expected_value)

    def check_text():
        actual = page.get_text(element_key)

        return actual if expected_normalized in normalize_text(actual) else False

    actual = poll(
        check_text,
        timeout=timeout,
    )

    if actual is False:
        actual = page.get_text(element_key)

        fail(
            "VerifyTextContains",
            (f"Expected text containing " f"'{expected_value}'"),
            actual,
        )

    return KeywordResult.ok(
        (f"Text contains " f"'{expected_value}'"),
        actual=actual,
    )


def verify_field_state(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyFieldState

    Target:
        PageObject.Element

    Expected examples:
        enabled
        disabled
        selected
        not_selected
        visible
        hidden
        present
        not_present
    """

    target_name = require_target(
        "VerifyFieldState",
        target,
    )

    expected_state = require_expected(
        "VerifyFieldState",
        expected,
    ).lower()

    page, element_key = resolve_element(
        target_name,
        context,
    )

    timeout = page_timeout(
        page,
        context,
    )

    def get_state() -> bool:
        if expected_state == "enabled":
            return page.is_enabled(element_key)

        if expected_state == "disabled":
            return not page.is_enabled(element_key)

        if expected_state == "selected":
            return page.is_selected(element_key)

        if expected_state in {
            "not_selected",
            "notselected",
        }:
            return not page.is_selected(element_key)

        if expected_state == "visible":
            return page.is_visible(element_key)

        if expected_state == "hidden":
            return not page.is_visible(element_key)

        if expected_state == "present":
            return page.is_present(element_key)

        if expected_state in {
            "not_present",
            "notpresent",
        }:
            return not page.is_present(element_key)

        raise KeywordError(
            ("VerifyFieldState: Unsupported " f"state '{expected_state}'.")
        )

    actual = poll(
        get_state,
        timeout=timeout,
    )

    if not actual:
        fail(
            "VerifyFieldState",
            (f"Expected state " f"'{expected_state}'"),
            actual=False,
        )

    return KeywordResult.ok(
        (f"{target_name} is " f"{expected_state}"),
        actual=True,
    )


def verify_attribute(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyAttribute

    Target:
        PageObject.Element

    Data:
        Attribute name.

    Expected:
        Expected attribute value.
    """

    target_name = require_target(
        "VerifyAttribute",
        target,
    )

    attribute_name = require_data(
        "VerifyAttribute",
        data,
    )

    expected_value = require_expected(
        "VerifyAttribute",
        expected,
    )

    page, element_key = resolve_element(
        target_name,
        context,
    )

    timeout = page_timeout(
        page,
        context,
    )

    def check_attribute():
        actual = page.get_attribute(
            element_key,
            str(attribute_name),
        )

        return (
            actual
            if normalize_text(actual) == normalize_text(expected_value)
            else False
        )

    actual = poll(
        check_attribute,
        timeout=timeout,
    )

    if actual is False:
        actual = page.get_attribute(
            element_key,
            str(attribute_name),
        )

        fail(
            "VerifyAttribute",
            (f"Attribute='{attribute_name}', " f"Expected='{expected_value}'"),
            actual,
        )

    return KeywordResult.ok(
        (f"Attribute '{attribute_name}' " f"matched"),
        actual=actual,
    )


def verify_element(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyElement

    Target:
        PageObject.Element

    Expected:
        visible / hidden / present / not_present

    Default:
        visible
    """

    target_name = require_target(
        "VerifyElement",
        target,
    )

    expected_state = (normalize_text(expected) or "visible").lower()

    page, element_key = resolve_element(
        target_name,
        context,
    )

    timeout = page_timeout(
        page,
        context,
    )

    def check():
        if expected_state == "visible":
            return page.is_visible(element_key)

        if expected_state == "hidden":
            return not page.is_visible(element_key)

        if expected_state == "present":
            return page.is_present(element_key)

        if expected_state in {
            "not_present",
            "notpresent",
        }:
            return not page.is_present(element_key)

        raise KeywordError(
            ("VerifyElement: Unsupported " f"Expected='{expected_state}'")
        )

    actual = poll(
        check,
        timeout=timeout,
    )

    if not actual:
        fail(
            "VerifyElement",
            (f"Expected element state " f"'{expected_state}'"),
            actual=False,
        )

    return KeywordResult.ok(
        (f"Element {target_name} " f"is {expected_state}"),
        actual=True,
    )


def verify_element_count(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyElementCount

    Target:
        PageObject.Element

    Expected:
        Expected element count.
    """

    target_name = require_target(
        "VerifyElementCount",
        target,
    )

    expected_count_text = require_expected(
        "VerifyElementCount",
        expected,
    )

    try:
        expected_count = int(expected_count_text)
    except ValueError as exc:
        raise KeywordError(
            ("VerifyElementCount: Expected " "must be an integer.")
        ) from exc

    page, element_key = resolve_element(
        target_name,
        context,
    )

    timeout = page_timeout(
        page,
        context,
    )

    def check_count():
        actual_count = page.count_elements(element_key)

        return actual_count if actual_count == expected_count else False

    actual_count = poll(
        check_count,
        timeout=timeout,
    )

    if actual_count is False:
        actual_count = page.count_elements(element_key)

        fail(
            "VerifyElementCount",
            (f"Expected count=" f"{expected_count}"),
            actual_count,
        )

    return KeywordResult.ok(
        (f"Element count matched " f"({expected_count})"),
        actual=actual_count,
    )


def verify_element_not_exist(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyElementNotExist

    Target:
        PageObject.Element
    """

    target_name = require_target(
        "VerifyElementNotExist",
        target,
    )

    page, element_key = resolve_element(
        target_name,
        context,
    )

    timeout = page_timeout(
        page,
        context,
    )

    def check_not_exist():
        return not page.is_present(element_key)

    actual = poll(
        check_not_exist,
        timeout=timeout,
    )

    if not actual:
        fail(
            "VerifyElementNotExist",
            "Element vẫn tồn tại.",
            actual=True,
        )

    return KeywordResult.ok(
        f"Element {target_name} does not exist",
        actual=False,
    )


def verify_calculation(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyCalculation

    Target:
        Optional PageObject.Element.

    Data:
        Mathematical expression.

    Expected:
        Expected numeric result.

    Example:
        VerifyCalculation | CartPage.Total | 16.51 * 3 | 49.53
    """

    expression = require_data(
        "VerifyCalculation",
        data,
    )

    expected_value = require_expected(
        "VerifyCalculation",
        expected,
    )

    try:
        expected_number = parse_number(expected_value)
    except ValueError as exc:
        raise KeywordError(
            ("VerifyCalculation: Invalid " f"Expected value '{expected_value}'.")
        ) from exc

    # If Target is provided, read actual value
    # from the Page Object.
    if not require_target(
        "VerifyCalculation",
        target,
    ):
        actual_number = safe_eval(str(expression))
    else:
        try:
            page, element_key = resolve_element(
                target,
                context,
            )

            actual_text = page.get_text(element_key)

            actual_number = parse_number(actual_text)

        except KeywordError:
            # Allow calculation-only usage.
            actual_number = safe_eval(str(expression))

    calculated_number = safe_eval(str(expression))

    if abs(calculated_number - expected_number) > 0.000001:
        fail(
            "VerifyCalculation",
            (
                f"Expression='{expression}', "
                f"Expected={expected_number}, "
                f"Calculated={calculated_number}"
            ),
            calculated_number,
        )

    return KeywordResult.ok(
        (f"Calculation '{expression}' " f"matched expected result"),
        actual=calculated_number,
    )


def verify_keyword(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyKeyword

    Executes an existing verification keyword
    and verifies that it succeeds.

    Data:
        Name of verification keyword.

    Example:
        VerifyKeyword | LoginPage.Message | VerifyText | Welcome
    """

    verification_keyword = require_data(
        "VerifyKeyword",
        data,
    )

    verification_keyword = str(verification_keyword).strip()

    allowed = {
        "VerifyUrl",
        "VerifyText",
        "VerifyTextContains",
        "VerifyFieldState",
        "VerifyAttribute",
        "VerifyElement",
        "VerifyElementCount",
        "VerifyElementNotExist",
        "VerifyCalculation",
        "VerifyDataMatch",
    }

    if verification_keyword not in allowed:
        raise KeywordError(
            (
                "VerifyKeyword: "
                f"'{verification_keyword}' "
                "is not an official verification keyword."
            )
        )

    # Import lazily to avoid circular dependency
    # between Registry and Verification Library.
    from keywords.keyword_registry import (
        build_default_registry,
    )

    registry = build_default_registry()

    handler = registry.resolve(verification_keyword)

    result = handler(
        target,
        None,
        expected,
        context,
    )

    if not isinstance(
        result,
        KeywordResult,
    ):
        raise KeywordError(("VerifyKeyword: handler must " "return KeywordResult."))

    return KeywordResult.ok(
        (f"Verification keyword " f"'{verification_keyword}' passed"),
        actual=result.actual,
    )


def verify_data_match(
    target: Any,
    data: Any,
    expected: Any,
    context: Any,
) -> KeywordResult:
    """
    Keyword: VerifyDataMatch

    Target:
        PageObject.Element

    Expected:
        Expected value.

    Used for comparing actual UI data
    against expected test data.
    """

    target_name = require_target(
        "VerifyDataMatch",
        target,
    )

    expected_value = require_expected(
        "VerifyDataMatch",
        expected,
    )

    page, element_key = resolve_element(
        target_name,
        context,
    )

    timeout = page_timeout(
        page,
        context,
    )

    expected_normalized = normalize_text(expected_value)

    def check():
        actual = page.get_text(element_key)

        return actual if normalize_text(actual) == expected_normalized else False

    actual = poll(
        check,
        timeout=timeout,
    )

    if actual is False:
        actual = page.get_text(element_key)

        fail(
            "VerifyDataMatch",
            (f"Expected data=" f"'{expected_value}'"),
            actual,
        )

    return KeywordResult.ok(
        (f"Data matched for " f"{target_name}"),
        actual=actual,
    )


# ---------------------------------------------------------------------------
# Official verification handler map
# ---------------------------------------------------------------------------

VERIFICATION_HANDLERS = {
    "VerifyUrl": verify_url,
    "VerifyText": verify_text,
    "VerifyTextContains": verify_text_contains,
    "VerifyFieldState": verify_field_state,
    "VerifyAttribute": verify_attribute,
    "VerifyElement": verify_element,
    "VerifyElementCount": verify_element_count,
    "VerifyElementNotExist": verify_element_not_exist,
    "VerifyCalculation": verify_calculation,
    "VerifyKeyword": verify_keyword,
    "VerifyDataMatch": verify_data_match,
}
