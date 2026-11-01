"""Search tests using the same hybrid reader/executor/context as test_login.py."""

from pathlib import Path
import allure
import pytest
from core.executor_test import TestExecutor
from utils.hybrid_reader import read_hybrid_cases

pytestmark = pytest.mark.functional
SEARCH_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "excel" / "search_hybrid.xlsx"
)
CASES = [
    case
    for case in read_hybrid_cases(SEARCH_FILE)
    if case["case_id"].startswith("SEARCH_")
]
if not CASES:
    raise ValueError(f"No SEARCH_* test cases in {SEARCH_FILE}")


@pytest.mark.parametrize(
    "case", CASES, ids=lambda item: f"{item['website']}_{item['case_id']}"
)
def test_search(context, case):
    allure.dynamic.title(f"{case['case_id']} - {case['website']} - Search")
    allure.dynamic.feature("Search")
    allure.dynamic.parameter("website", case["website"])
    allure.dynamic.parameter("template_id", case["template_id"])
    if isinstance(context, dict):
        context["website"] = case["website"]
        context.pop("_search_state", None)
    else:
        context.website = case["website"]
        context._search_state = {}
    TestExecutor(context).run(case["steps"])
