from types import SimpleNamespace

import pytest

from keywords import business_keywords
from keywords.keyword_utils import KeywordError


def test_add_to_cart_keyword_passes_product_and_quantity(monkeypatch):
    calls = []
    page = SimpleNamespace(add_to_cart=lambda *args: calls.append(args))
    monkeypatch.setattr(
        business_keywords, "resolve_target", lambda target, context: (page, None)
    )

    result = business_keywords.add_to_cart(
        "product", "Fresh Carrots|2", "", object()
    )

    assert result.status == "PASS"
    assert calls == [("Fresh Carrots", 2)]


@pytest.mark.parametrize(
    "data", ["Fresh Carrots", "|2", "Fresh Carrots|0", "Fresh Carrots|x"]
)
def test_add_to_cart_keyword_rejects_invalid_selection(monkeypatch, data):
    calls = []
    page = SimpleNamespace(add_to_cart=lambda *args: calls.append(args))
    monkeypatch.setattr(
        business_keywords, "resolve_target", lambda target, context: (page, None)
    )

    with pytest.raises(KeywordError, match="AddToCart: "):
        business_keywords.add_to_cart("product", data, "", object())

    assert calls == []
