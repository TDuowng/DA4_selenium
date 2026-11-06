import pandas as pd

from config import EXCEL_DIR
from utils.hybrid_reader import build_cases, read_hybrid_cases, records


def test_cart_cases_use_site_login_url():
    cases = read_hybrid_cases(EXCEL_DIR / "cart_hybrid.xlsx")
    spcart_cases = [case for case in cases if case["website"] == "spcart"]

    assert len(spcart_cases) >= 2
    assert all(
        case["login_url"]
        == "https://simple-shopping-cart-steel-six.vercel.app/#admin"
        for case in spcart_cases
    )
    assert all("login_url" not in case["case_data"] for case in spcart_cases)


def test_case_login_url_overrides_site_and_empty_site_uses_base_url():
    sheets = pd.read_excel(
        EXCEL_DIR / "cart_hybrid.xlsx",
        sheet_name=["test_steps", "test_cases", "sites"],
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )
    case_rows = records(sheets["test_cases"])
    site_rows = records(sheets["sites"])
    for row in case_rows:
        if row["case_id"] == "CART_SPCART_01":
            row["login_url"] = "https://override.example.test/login"
    for row in site_rows:
        if row["site_id"] == "qabrains":
            row["login_url"] = ""

    cases = {
        case["case_id"]: case
        for case in build_cases(records(sheets["test_steps"]), case_rows, site_rows)
    }
    assert cases["CART_SPCART_01"]["login_url"] == (
        "https://override.example.test/login"
    )
    assert cases["CART_SPCART_02"]["login_url"] == (
        "https://simple-shopping-cart-steel-six.vercel.app/#admin"
    )
    assert cases["CART_QABRAINS_01"]["login_url"] == (
        cases["CART_QABRAINS_01"]["site_url"]
    )
