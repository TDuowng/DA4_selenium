import pytest

from framework.config import EXCEL_FILE
from framework.core.keyword_engine import KeywordEngine
from framework.utils.hybrid_reader import read_hybrid_cases

CASES = [c for c in read_hybrid_cases(EXCEL_FILE) if c["case_id"].startswith("LOGIN_")]
assert CASES, "Không tìm thấy case LOGIN_* trong sheet test_case"


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["case_id"])
def test_login(context, case):
    KeywordEngine(context).run(case["steps"])
