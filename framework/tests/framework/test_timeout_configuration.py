from types import SimpleNamespace

from config import TIMEOUT
from keywords.keyword_utils import page_timeout
from keywords.target_resolver import resolve_page


def test_login_page_uses_context_timeout_for_element_and_verification_waits():
    context = SimpleNamespace(
        driver=object(),
        website="demoQA",
        site_url="https://example.test/login",
        timeout=7,
    )

    page = resolve_page("login", context)

    assert page.wait._timeout == 7
    assert page_timeout(page, context) == 7


def test_login_page_uses_shared_default_when_context_has_no_timeout():
    context = {
        "driver": object(),
        "website": "demoQA",
        "site_url": "https://example.test/login",
    }

    page = resolve_page("login", context)

    assert page.wait._timeout == TIMEOUT
    assert page_timeout(page, context) == TIMEOUT
