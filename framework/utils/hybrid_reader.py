# EXCEL HYBRID: test_steps là template; test_case là input/expected từng ca.
# Toàn bộ dữ liệu được kiểm tra lúc collect, TRƯỚC khi fixture mở Chrome.
# Không sort để che lỗi thứ tự step, không return [] để biến lỗi thành skip.
import pandas as pd
from config import SITE_CONFIG

from utils.template_binding import (
    TEMPLATE_FIELDS,
    bind_template,
    validate_template,
)

STEPS_SHEET = "test_steps"
CASES_SHEET = "test_cases"
REQUIRED_CASE_FIELDS = {
    "case_id",
    "template_id",
    "website",
}  # các cột còn lại tuỳ template


def records(frame):
    rows = frame.to_dict("records")
    # Bỏ dòng trống hoàn toàn (Excel hay để thừa cuối sheet); dòng trống một phần vẫn bị kiểm tra
    return [r for r in rows if any(v != "" for v in r.values())]


def build_cases(template_rows, data_rows):
    """Join theo template_id: một dòng test_case -> một case."""

    if not template_rows or not data_rows:
        raise ValueError(f"{STEPS_SHEET}/{CASES_SHEET} không được rỗng")

    templates = {}

    for row in template_rows:
        if set(row) != TEMPLATE_FIELDS:
            raise ValueError(f"{STEPS_SHEET} sai schema")

        templates.setdefault(row["template_id"], []).append(row)

    for template in templates.values():
        validate_template(template)

    cases, seen, referenced = [], set(), set()

    for row in data_rows:
        if not REQUIRED_CASE_FIELDS <= set(row):
            raise ValueError(
                f"{CASES_SHEET} thiếu cột " f"{sorted(REQUIRED_CASE_FIELDS - set(row))}"
            )

        case_id = row["case_id"]
        template_id = row["template_id"]

        # Đọc website từ Excel
        website = str(row["website"]).strip()

        # Kiểm tra website hợp lệ
        if website not in SITE_CONFIG:
            raise ValueError(
                f"Case {case_id}: website '{website}' "
                f"không hợp lệ. "
                f"Website hỗ trợ: {list(SITE_CONFIG)}"
            )

        if not case_id or case_id in seen:
            raise ValueError(f"case_id rỗng hoặc trùng: {case_id!r}")

        if template_id not in templates:
            raise ValueError(
                f"Case {case_id}: template không tồn tại: " f"{template_id!r}"
            )

        seen.add(case_id)
        referenced.add(template_id)

        # Bind template với dữ liệu test case
        steps = bind_template(templates[template_id], row)

        # Truyền website vào test case
        cases.append(
            {
                "case_id": case_id,
                "template_id": template_id,
                "website": website,
                "steps": steps,
            }
        )

    unused = set(templates) - referenced

    if unused:
        raise ValueError(f"Template chưa có dữ liệu: {sorted(unused)}")

    return cases


def read_hybrid_cases(path):
    # dtype=str + keep_default_na=False: giữ ô rỗng là "", giữ "NA"/"0123"; KHÔNG trim dữ liệu
    sheets = pd.read_excel(
        path,
        sheet_name=[STEPS_SHEET, CASES_SHEET],
        dtype=str,
        keep_default_na=False,
        engine="openpyxl",
    )
    if set(sheets[STEPS_SHEET].columns) != TEMPLATE_FIELDS:
        raise ValueError(f"{STEPS_SHEET} thiếu/thừa cột")
    return build_cases(records(sheets[STEPS_SHEET]), records(sheets[CASES_SHEET]))
