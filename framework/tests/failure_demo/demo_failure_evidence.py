# ============================================================
# DEMO CỐ Ý FAIL: FAILURE EVIDENCE
# File không khớp python_files = test_*.py nên KHÔNG chạy trong suite mặc định.
# Chạy riêng:
#   pytest tests/failure_demo/demo_failure_evidence.py --observe-seconds=0
# Kết quả mong đợi: 1 test FAIL, có PNG + HTML + category trong junit.xml
# ============================================================
from copy import deepcopy

import allure
import pytest

from config import EXCEL_FILE
from core.executor_test import (
    TestExecutor as CaseExecutor,
)  # đổi nếu file của bạn tên khác
from utils.hybrid_reader import read_hybrid_cases

pytestmark = pytest.mark.failure_demo


def test_intentional_wrong_expected(context):
    cases = read_hybrid_cases(EXCEL_FILE)
    # deepcopy để không làm hỏng dữ liệu đã bind của các test khác.
    case = deepcopy(next(c for c in cases if c["case_id"].startswith("LOGIN_")))
    step = next(r for r in case["steps"] if r["keyword"].lower().startswith("verify"))
    step["expected"] = "SAI_CO_CHU_DICH"

    allure.dynamic.title(f"{case['case_id']} - Demo fail có chủ đích")
    allure.dynamic.feature("Failure Evidence")
    CaseExecutor(context).run(case["steps"])
