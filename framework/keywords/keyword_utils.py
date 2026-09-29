from __future__ import annotations

import ast
import operator
import re
from dataclasses import dataclass
from typing import Any, Callable


class KeywordError(Exception):
    """Base exception for keyword execution errors."""


class VerificationFailed(KeywordError):
    """Raised when a verification keyword fails."""


@dataclass(frozen=True)
class KeywordResult:
    """
    Standard result returned by a keyword.

    status:
        PASS / FAIL

    message:
        Human-readable execution result.

    actual:
        Actual value produced by the keyword, if available.
    """

    status: str
    message: str
    actual: Any = None

    @classmethod
    def ok(
        cls,
        message: str,
        actual: Any = None,
    ) -> "KeywordResult":
        return cls(
            status="PASS",
            message=message,
            actual=actual,
        )

    @classmethod
    def fail(
        cls,
        message: str,
        actual: Any = None,
    ) -> "KeywordResult":
        return cls(
            status="FAIL",
            message=message,
            actual=actual,
        )


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def is_blank(value: Any) -> bool:
    """
    Return True when value is None or contains only whitespace.
    """
    return value is None or (
        isinstance(value, str) and not value.strip()
    )


def to_text(value: Any) -> str:
    """
    Convert a value to normalized text representation.
    """
    if value is None:
        return ""

    return str(value).strip()


def normalize_text(value: Any) -> str:
    """
    Normalize text for verification.

    - Convert to string
    - Strip leading/trailing spaces
    - Collapse consecutive whitespace
    """
    text = to_text(value)

    return re.sub(r"\s+", " ", text).strip()


def require_target(
    keyword: str,
    target: Any,
) -> str:
    """
    Validate and return Target as text.
    """
    if is_blank(target):
        raise KeywordError(
            f"{keyword}: Target không được để trống."
        )

    return to_text(target)


def require_data(
    keyword: str,
    data: Any,
) -> Any:
    """
    Validate Data.

    Data may legitimately be an empty string in some keywords,
    therefore only None is considered missing here.
    """
    if data is None:
        raise KeywordError(
            f"{keyword}: Data không được để trống."
        )

    if isinstance(data, str) and not data.strip():
        raise KeywordError(
            f"{keyword}: Data không được để trống."
        )

    return data


def require_expected(
    keyword: str,
    expected: Any,
) -> str:
    """
    Validate Expected value for verification keywords.
    """
    if is_blank(expected):
        raise KeywordError(
            f"{keyword}: Expected không được để trống."
        )

    return to_text(expected)


# ---------------------------------------------------------------------------
# Target helpers
# ---------------------------------------------------------------------------

def resolve_page(
    target: Any,
    context: Any,
):
    """
    Resolve Target and require it to be a Page Object.
    """
    from keywords.target_resolver import (
        TargetError,
        resolve_target,
    )

    target_name = require_target(
        "ResolvePage",
        target,
    )

    try:
        page, element_key = resolve_target(
            target_name,
            context,
        )
    except (TargetError, KeyError) as exc:
        raise KeywordError(
            f"Không thể resolve Page '{target_name}': {exc}"
        ) from exc

    if element_key is not None:
        raise KeywordError(
            f"Target phải là Page Object, "
            f"không phải element: '{target_name}'"
        )

    return page


def resolve_element(
    target: Any,
    context: Any,
):
    """
    Resolve Target and require it to be an element
    belonging to a Page Object.
    """
    from keywords.target_resolver import (
        TargetError,
        resolve_target,
    )

    target_name = require_target(
        "ResolveElement",
        target,
    )

    try:
        page, element_key = resolve_target(
            target_name,
            context,
        )
    except (TargetError, KeyError) as exc:
        raise KeywordError(
            f"Không thể resolve Element '{target_name}': {exc}"
        ) from exc

    if element_key is None:
        raise KeywordError(
            f"Target phải là Element, "
            f"không phải Page Object: '{target_name}'"
        )

    return page, element_key


# ---------------------------------------------------------------------------
# Wait / polling helpers
# ---------------------------------------------------------------------------

def page_timeout(
    page: Any,
    context: Any,
    default: float = 10.0,
) -> float:
    """
    Get timeout from context/page configuration.

    Priority:
        context.timeout
        page.timeout
        default
    """

    timeout = getattr(
        context,
        "timeout",
        None,
    )

    if timeout is None:
        timeout = getattr(
            page,
            "timeout",
            None,
        )

    if timeout is None:
        timeout = default

    try:
        timeout = float(timeout)
    except (TypeError, ValueError):
        timeout = default

    return max(timeout, 0.1)


def poll(
    condition: Callable[[], Any],
    timeout: float = 10.0,
    interval: float = 0.2,
) -> Any:
    """
    Poll a condition until it returns a truthy value.

    No time.sleep() is used here.

    The condition is expected to return:
        truthy -> success
        falsy  -> continue waiting
    """

    from time import monotonic

    deadline = monotonic() + timeout
    last_exception: Exception | None = None

    while monotonic() < deadline:
        try:
            result = condition()

            if result:
                return result

        except Exception as exc:
            last_exception = exc

        # Short wait without using time.sleep().
        import threading

        remaining = deadline - monotonic()

        if remaining <= 0:
            break

        threading.Event().wait(
            min(interval, remaining)
        )

    if last_exception is not None:
        raise last_exception

    return False


def fail(
    keyword: str,
    message: str,
    actual: Any = None,
) -> None:
    """
    Raise a standardized verification failure.
    """
    raise VerificationFailed(
        f"{keyword}: {message}"
        + (
            f" | Actual={actual!r}"
            if actual is not None
            else ""
        )
    )


# ---------------------------------------------------------------------------
# Calculation helpers
# ---------------------------------------------------------------------------

def parse_number(
    value: Any,
) -> float:
    """
    Convert a value into a number.

    Supports:
        10
        "10"
        "10.5"
        "$49.53"
        "1,000.50"
    """

    if isinstance(value, bool):
        raise ValueError(
            f"Boolean is not a valid number: {value!r}"
        )

    if isinstance(value, (int, float)):
        return float(value)

    text = to_text(value)

    if not text:
        raise ValueError(
            "Cannot parse blank value as number."
        )

    text = (
        text.replace(",", "")
        .replace("$", "")
        .replace("€", "")
        .replace("£", "")
        .replace("%", "")
        .strip()
    )

    return float(text)


_ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(
    expression: str,
) -> float:
    """
    Safely evaluate a mathematical expression.

    Supported:
        + - * / % **
        parentheses
        numeric values

    Examples:
        safe_eval("10 + 5")
        safe_eval("(10 + 5) * 2")
    """

    if is_blank(expression):
        raise ValueError(
            "Calculation expression cannot be blank."
        )

    tree = ast.parse(
        str(expression),
        mode="eval",
    )

    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(
                node.value,
                (int, float),
            ) and not isinstance(
                node.value,
                bool,
            ):
                return float(node.value)

            raise ValueError(
                "Only numeric constants are allowed."
            )

        if isinstance(node, ast.BinOp):
            operation = _ALLOWED_OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    f"Unsupported operator: "
                    f"{type(node.op).__name__}"
                )

            left = evaluate(node.left)
            right = evaluate(node.right)

            return float(
                operation(left, right)
            )

        if isinstance(node, ast.UnaryOp):
            operation = _ALLOWED_OPERATORS.get(
                type(node.op)
            )

            if operation is None:
                raise ValueError(
                    f"Unsupported unary operator: "
                    f"{type(node.op).__name__}"
                )

            return float(
                operation(
                    evaluate(node.operand)
                )
            )

        raise ValueError(
            f"Unsupported expression node: "
            f"{type(node).__name__}"
        )

    return evaluate(tree)