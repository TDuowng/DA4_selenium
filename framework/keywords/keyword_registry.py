# keywords/keyword_registry.py
from __future__ import annotations


import re
from typing import Any, Callable

from .common_keywords import (
    navigate,
    set_text,
    clear_text,
    click_element,
    click_outside,
    select_option,
)

from .business_keywords import (
    login,
    add_to_cart,
    set_product_out_of_stock,
)

from .verification_keywords import (
    verify_url,
    verify_text,
    verify_text_contains,
    verify_field_state,
    verify_attribute,
    verify_element,
    verify_element_count,
    verify_element_not_exist,
    verify_calculation,
    verify_keyword,
    verify_data_match,
)

KeywordHandler = Callable[
    [Any, Any, Any, Any],
    Any,
]


OFFICIAL_KEYWORDS = {
    "Navigate",
    "SetText",
    "ClearText",
    "ClickElement",
    "ClickOutside",
    "SelectOption",
    "Login",
    "AddToCart",
    "SetProductOutOfStock",
    "VerifyUrl",
    "VerifyText",
    "VerifyTextContains",
    "VerifyFieldState",
    "VerifyAttribute",
    "VerifyElement",
    "VerifyElementCount",
    "VerifyElementNotExist",
    "VerifyCalculation",
    "VerifyKeyword",
    "VerifyDataMatch",
}


LIFECYCLE_KEYWORDS = {
    "OpenBrowser",
    "CloseBrowser",
}


_PASCAL_CASE = re.compile(r"^[A-Z][A-Za-z0-9]*$")


KEYWORD_MAP: dict[str, KeywordHandler] = {
    # Common Keywords
    "Navigate": navigate,
    "SetText": set_text,
    "ClearText": clear_text,
    "ClickElement": click_element,
    "ClickOutside": click_outside,
    "SelectOption": select_option,
    # Business Keywords
    "Login": login,
    "AddToCart": add_to_cart,
    "SetProductOutOfStock": set_product_out_of_stock,
    # Verification Keywords
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


class KeywordRegistry:
    """
    Registry responsible for resolving keyword name
    to its handler function.
    """

    def __init__(
        self,
        keyword_map: dict[str, KeywordHandler] | None = None,
    ) -> None:
        self._keyword_map = (
            dict(keyword_map) if keyword_map is not None else dict(KEYWORD_MAP)
        )

    def resolve(self, keyword: str) -> KeywordHandler:
        if not isinstance(keyword, str):
            raise TypeError("Keyword must be a string")

        name = keyword.strip()

        if not name:
            raise KeyError("Keyword cannot be blank")

        if not _PASCAL_CASE.fullmatch(name):
            raise KeyError(
                f"Invalid keyword format: '{name}'. " "Keyword must use PascalCase."
            )

        try:
            return self._keyword_map[name]
        except KeyError as exc:
            raise KeyError(f"Keyword is not registered: '{name}'") from exc

    def is_registered(self, keyword: str) -> bool:
        return keyword in self._keyword_map

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self._keyword_map.keys())

    def __contains__(self, keyword: str) -> bool:
        return keyword in self._keyword_map

    def __len__(self) -> int:
        return len(self._keyword_map)


def build_default_registry() -> KeywordRegistry:
    """
    Build and validate the default Keyword Registry.
    """

    registry = KeywordRegistry()

    registered = set(registry.names)

    if registered != OFFICIAL_KEYWORDS:
        missing = OFFICIAL_KEYWORDS - registered
        extra = registered - OFFICIAL_KEYWORDS

        raise RuntimeError(
            "Keyword registry mismatch. "
            f"Missing={sorted(missing)}, "
            f"Extra={sorted(extra)}"
        )

    return registry
