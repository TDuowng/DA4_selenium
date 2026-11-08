"""Run Practice Form validation scenarios through the existing Hybrid pipeline."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from config import TIMEOUT, EXCEL_DIR
from core.executor_test import TestExecutor as CaseExecutor
from utils.hybrid_reader import read_hybrid_cases

EXCEL_FILE = EXCEL_DIR / "validation_hybrid.xlsx"


def _validation_cases():
    # Excel schema, keyword names and locators are checked during collection.
    return read_hybrid_cases(EXCEL_FILE)


@pytest.mark.parametrize(
    "test_case",
    [pytest.param(case, id=case["case_id"]) for case in _validation_cases()],
)
def test_validation(driver, test_case):
    context = SimpleNamespace(
        driver=driver,
        timeout=TIMEOUT,
        website=test_case["website"],
        site_url=test_case["site_url"],
    )
    assert CaseExecutor(context).run(test_case["steps"]) == "PASS"
