# ============================================================
# KIỂM THỬ ĐĂNG NHẬP (Hybrid: template Excel + dữ liệu từng ca)
# Đọc, validate, bind khi collection: chưa mở browser.
# ============================================================
import allure
import pytest

from config import EXCEL_FILE
from core.executor_test import (
    TestExecutor as CaseExecutor,
)  # đổi nếu file của bạn tên khác
from utils.hybrid_reader import read_hybrid_cases

pytestmark = pytest.mark.functional

CASE_PREFIX = "LOGIN_"

ALL_CASES = read_hybrid_cases(EXCEL_FILE)
CASES = [c for c in ALL_CASES if c["case_id"].startswith(CASE_PREFIX)]
if not CASES:
    raise ValueError(
        f"Không có case {CASE_PREFIX}* trong sheet test_case. "
        f"Hiện có: {[c['case_id'] for c in ALL_CASES]}"
    )


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["case_id"])
def test_login(context, case):
    allure.dynamic.title(f"{case['case_id']} - Login")
    allure.dynamic.feature("Login")
    allure.dynamic.parameter("template_id", case["template_id"])
    CaseExecutor(context).run(case["steps"])
