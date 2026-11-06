"""Cart smoke tests for the sites in the hybrid workbook."""

import allure
import pytest

from config import EXCEL_DIR
from core.executor_test import TestExecutor as CaseExecutor
from utils.hybrid_reader import read_hybrid_cases


pytestmark = pytest.mark.functional
CASES = read_hybrid_cases(EXCEL_DIR / "cart_hybrid.xlsx")


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["case_id"])
def test_cart(context, case):
    allure.dynamic.title(f"{case['case_id']} - {case['website']} - Cart")
    allure.dynamic.feature("Cart")
    context.website = case["website"]
    context.site_url = case["site_url"]
    context.login_url = case["login_url"]
    CaseExecutor(context).run(case["steps"])
