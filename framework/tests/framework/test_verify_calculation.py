from types import SimpleNamespace

import pytest

from keywords import verification_keywords
from keywords.keyword_utils import VerificationFailed


def test_calculation_with_no_target_checks_expression():
    result = verification_keywords.verify_calculation("", "16.51 * 3", "49.53", None)

    assert result.actual == pytest.approx(49.53)


def test_calculation_with_target_checks_ui_value(monkeypatch):
    page = SimpleNamespace(get_text=lambda element: "49.52")
    monkeypatch.setattr(
        verification_keywords,
        "resolve_element",
        lambda target, context: (page, "total"),
    )

    with pytest.raises(VerificationFailed, match="Calculated"):
        verification_keywords.verify_calculation(
            "CartPage.Total", "16.51 * 3", "49.53", None
        )


def test_calculation_does_not_ignore_invalid_target(monkeypatch):
    def invalid_target(target, context):
        raise ValueError("Unknown target")

    monkeypatch.setattr(verification_keywords, "resolve_element", invalid_target)

    with pytest.raises(ValueError, match="Unknown target"):
        verification_keywords.verify_calculation(
            "CartPage.Unknown", "16.51 * 3", "49.53", None
        )


def test_calculation_rejects_non_finite_expected():
    with pytest.raises(verification_keywords.KeywordError, match="Invalid Expected"):
        verification_keywords.verify_calculation("", "16.51 * 3", "nan", None)
