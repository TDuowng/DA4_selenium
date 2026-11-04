import allure
import pytest

from config import EXCEL_DIR
from core.executor_test import TestExecutor as CaseExecutor
from utils.hybrid_reader import read_hybrid_cases

pytestmark = pytest.mark.functional

EXCEL_FILE = EXCEL_DIR / "register_hybrid.xlsx"
CASES = read_hybrid_cases(EXCEL_FILE)


@pytest.mark.parametrize("case", CASES, ids=lambda c: f"{c['website']}_{c['case_id']}")
def test_register(context, case):
    allure.dynamic.title(f"{case['case_id']} - {case['website']} - Register")
    allure.dynamic.feature("Register")
    allure.dynamic.parameter("website", case["website"])
    allure.dynamic.parameter("template_id", case["template_id"])

    context.website = case["website"]
    context.site_url = case["site_url"]

    duplicate_field = case["case_data"].get("duplicate_field")
    if duplicate_field:
        if case["website"] != "taophoBA" or duplicate_field not in {
            "email",
            "username",
        }:
            raise ValueError(f"Unsupported duplicate setup: {duplicate_field}")
        # Mỗi WebDriver dùng một profile riêng: tạo user trùng trong localStorage
        # của chính phiên này trước khi chạy các bước đăng ký.
        seed = {
            "name": "Existing User",
            "email": "seed@example.test",
            "username": "seedUser",
            "phone": "0999999999",
            "password": "Seed@123",
            "role": "customer",
        }
        seed[duplicate_field] = case["case_data"][duplicate_field]
        context.driver.get(case["site_url"])
        context.driver.execute_script(
            "localStorage.setItem('users', JSON.stringify([arguments[0]]));",
            seed,
        )

    CaseExecutor(context).run(case["steps"])
