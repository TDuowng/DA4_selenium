"""Chạy các ca kiểm thử search từ Excel qua pipeline Hybrid hiện có."""

import allure
import pytest

from config import EXCEL_DIR
from core.executor_test import TestExecutor as CaseExecutor
from utils.hybrid_reader import read_hybrid_cases

pytestmark = pytest.mark.functional

SEARCH_EXCEL_FILE = EXCEL_DIR / "search_hybrid.xlsx"
CASE_PREFIX = "SEARCH_"

# Validate và bind khi collection, trước khi fixture khởi tạo WebDriver.
ALL_CASES = read_hybrid_cases(SEARCH_EXCEL_FILE)
CASES = [case for case in ALL_CASES if case["case_id"].startswith(CASE_PREFIX)]
if not CASES:
    raise ValueError(
        f"Không có case {CASE_PREFIX}* trong {SEARCH_EXCEL_FILE.name}. "
        f"Hiện có: {[case['case_id'] for case in ALL_CASES]}"
    )


@pytest.mark.parametrize(
    "case", CASES, ids=lambda case: f"{case['website']}_{case['case_id']}"
)
def test_search(context, case):
    """Thực thi nguyên thứ tự bước và kết quả mong đợi trong Excel."""
    allure.dynamic.title(f"{case['case_id']} - {case['website']} - Search")
    allure.dynamic.feature("Search")
    allure.dynamic.story(case["template_id"])
    allure.dynamic.parameter("website", case["website"])
    allure.dynamic.parameter("template_id", case["template_id"])

    if isinstance(context, dict):
        context["website"] = case["website"]
        context["site_url"] = case["site_url"]
    else:
        context.website = case["website"]
        context.site_url = case["site_url"]

    CaseExecutor(context).run(case["steps"])
