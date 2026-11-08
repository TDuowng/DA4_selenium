from types import SimpleNamespace

import pytest

from core.executor_test import _mask
from keywords import business_keywords
from keywords.keyword_utils import KeywordError
from pages.login_page import LoginPage


def test_login_keyword_passes_credentials_to_page(monkeypatch):
    calls = []
    page = SimpleNamespace(login=lambda *args: calls.append(args))
    monkeypatch.setattr(
        business_keywords, "resolve_target", lambda target, context: (page, None)
    )

    result = business_keywords.login(
        "login", "student@example.test/secret/with/slash", "", object()
    )

    assert result.status == "PASS"
    assert calls == [("student@example.test", "secret/with/slash")]


def test_login_keyword_preserves_default_credentials(monkeypatch):
    calls = []
    page = SimpleNamespace(login=lambda *args: calls.append(args))
    monkeypatch.setattr(
        business_keywords, "resolve_target", lambda target, context: (page, None)
    )

    business_keywords.login("login", "", "", object())

    assert calls == [()]


@pytest.mark.parametrize("data", ["username", "/password", "username/"])
def test_login_keyword_rejects_incomplete_credentials(monkeypatch, data):
    calls = []
    page = SimpleNamespace(login=lambda *args: calls.append(args))
    monkeypatch.setattr(
        business_keywords, "resolve_target", lambda target, context: (page, None)
    )

    with pytest.raises(KeywordError, match="Login: "):
        business_keywords.login("login", data, "", object())

    assert calls == []


def test_login_keyword_masks_credentials_in_step_title():
    row = {
        "keyword": "Login",
        "target": "login",
        "data": "student@example.test/secret",
    }

    assert _mask(row) == "***"


def test_spcart_login_uses_admin_credentials(monkeypatch):
    calls = []
    page = LoginPage.__new__(LoginPage)
    page.website = "spcart"
    page.URL = "https://simple-shopping-cart-steel-six.vercel.app/#admin"
    monkeypatch.setattr(
        page,
        "wait",
        SimpleNamespace(until=lambda condition: calls.append(("wait", condition))),
        raising=False,
    )

    monkeypatch.setattr(page, "open", lambda: calls.append(("open", page.URL)))
    monkeypatch.setattr(page, "click", lambda key: calls.append(("click", key)))
    monkeypatch.setattr(
        page,
        "enter_text",
        lambda key, value: calls.append(("enter_text", key, value)),
    )
    monkeypatch.setattr(page, "locator", lambda key: ("css selector", key))

    page.login("admin", "admin123")

    assert calls[:5] == [
        ("open", page.URL),
        ("click", "openLogin"),
        ("enter_text", "username", "admin"),
        ("enter_text", "password", "admin123"),
        ("click", "loginButton"),
    ]
    assert [call[0] for call in calls[5:]] == ["wait", "wait"]
