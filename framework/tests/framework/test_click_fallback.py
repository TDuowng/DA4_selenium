from types import SimpleNamespace

import pytest
from selenium.common.exceptions import ElementClickInterceptedException

from pages.register_page import RegisterPage
from pages.validation_page import ValidationPage


@pytest.mark.parametrize(
    ("page_class", "site", "element"),
    [
        (ValidationPage, "demoQA", "submit"),
        (RegisterPage, "taophoBA", "registerButton"),
    ],
)
def test_allowed_click_uses_dom_after_interception(
    monkeypatch, page_class, site, element
):
    page = page_class.__new__(page_class)
    page.locator_sheet = site
    button = object()
    calls = []
    page.driver = SimpleNamespace(
        execute_script=lambda script, item: calls.append((script, item))
    )
    monkeypatch.setattr(page, "locator", lambda key: ("id", key))
    monkeypatch.setattr(page, "find_element", lambda locator: button)

    def intercepted_click(locator):
        calls.append(("native", locator))
        raise ElementClickInterceptedException()

    monkeypatch.setattr(page, "click_element", intercepted_click)

    page.click(element)

    assert calls == [
        ("native", ("id", element)),
        ("arguments[0].click();", button),
    ]


@pytest.mark.parametrize(
    ("page_class", "site", "element"),
    [
        (ValidationPage, "demoQA", "genderMale"),
        (RegisterPage, "taophoBA", "otherButton"),
        (RegisterPage, "demoQA", "registerButton"),
    ],
)
def test_other_clicks_keep_interception_error(
    monkeypatch, page_class, site, element
):
    page = page_class.__new__(page_class)
    page.locator_sheet = site
    monkeypatch.setattr(page, "locator", lambda key: ("id", key))

    def intercepted_click(locator):
        raise ElementClickInterceptedException()

    monkeypatch.setattr(page, "click_element", intercepted_click)

    with pytest.raises(ElementClickInterceptedException):
        page.click(element)


def test_successful_native_click_does_not_use_fallback(monkeypatch):
    page = ValidationPage.__new__(ValidationPage)
    page.locator_sheet = "demoQA"
    calls = []
    monkeypatch.setattr(page, "locator", lambda key: ("id", key))
    monkeypatch.setattr(page, "click_element", lambda locator: calls.append(locator))

    page.click("submit")

    assert calls == [("id", "submit")]
