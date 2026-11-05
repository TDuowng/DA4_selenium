"""Kiểm tra search chọn đúng site mà không khởi tạo browser."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from keywords.target_resolver import resolve_page

pytestmark = pytest.mark.framework


@pytest.mark.parametrize("page_name", ["search", "books", "book"])
@pytest.mark.parametrize("website", ["demoQA", "taophoBA"])
@pytest.mark.parametrize("as_dict", [True, False])
def test_search_page_uses_case_site(monkeypatch, page_name, website, as_dict):
    reader = Mock()
    monkeypatch.setattr("pages.base_page.get_locator_reader", lambda _: reader)
    driver = Mock()
    url = f"https://example.test/{website}/catalog"
    values = {"driver": driver, "website": website, "site_url": url}
    context = values if as_dict else SimpleNamespace(**values)

    page = resolve_page(page_name, context)
    page.open()
    page.locator("title")

    driver.get.assert_called_once_with(url)
    reader.get_locator.assert_called_once_with(
        "book" if page_name == "book" else "search", "title", sheet=website
    )


def test_search_page_requires_case_url(monkeypatch):
    reader = Mock()
    monkeypatch.setattr("pages.base_page.get_locator_reader", lambda _: reader)
    context = {"driver": Mock(), "website": "demoQA"}

    with pytest.raises(ValueError, match="sheet sites"):
        resolve_page("search", context)
