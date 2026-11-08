"""Kiểm tra search chọn đúng site mà không khởi tạo browser."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from keywords.target_resolver import TargetError, resolve_page

pytestmark = pytest.mark.framework


@pytest.mark.parametrize("website", ["demoQA", "taophoBA"])
@pytest.mark.parametrize("as_dict", [True, False])
def test_search_page_uses_case_site(monkeypatch, website, as_dict):
    reader = Mock()
    monkeypatch.setattr("pages.base_page.get_locator_reader", lambda _: reader)
    driver = Mock()
    url = f"https://example.test/{website}/catalog"
    values = {"driver": driver, "website": website, "site_url": url}
    context = values if as_dict else SimpleNamespace(**values)

    page = resolve_page("search", context)
    page.open()
    page.locator("title")

    driver.get.assert_called_once_with(url)
    reader.get_locator.assert_called_once_with(
        "search", "title", sheet=website
    )


@pytest.mark.parametrize("page_name", ["book", "books"])
def test_unknown_page_names_are_rejected(page_name):
    context = {
        "driver": Mock(),
        "website": "demoQA",
        "site_url": "https://example.test",
    }

    with pytest.raises(TargetError, match="Page Object module"):
        resolve_page(page_name, context)


def test_search_page_requires_case_url(monkeypatch):
    reader = Mock()
    monkeypatch.setattr("pages.base_page.get_locator_reader", lambda _: reader)
    context = {"driver": Mock(), "website": "demoQA"}

    with pytest.raises(TargetError, match="sheet sites"):
        resolve_page("search", context)
