# HYBRID BINDING: ghép template với MỘT dòng test_case, không mở browser.
# Chỉ hỗ trợ placeholder chiếm toàn ô như {username}; chưa có ngôn ngữ biểu thức.
import re

from framework.config import LOCATOR_FILE
from framework.keywords.keyword_registry import build_default_registry
from framework.keywords.keyword_spec import KEYWORD_SPEC, START_KEYWORDS
from framework.keywords.target_resolver import TargetError, load_page_class
from framework.utils.locator_reader import get_locator_reader

REGISTRY = build_default_registry()

TEMPLATE_FIELDS = {"template_id", "step", "keyword", "target", "data", "expected"}
PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")
ELEMENT_TARGET = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)")

assert set(KEYWORD_SPEC) <= set(REGISTRY.names), "KEYWORD_SPEC có keyword chưa đăng ký"


def _validate_target(where, keyword, target):
    kind = KEYWORD_SPEC[keyword].target if keyword in KEYWORD_SPEC else "any"
    if kind == "any":
        return
    if kind == "none":
        if target:
            raise ValueError(f"{where}: {keyword} không dùng Target")
        return
    if kind == "page":
        if "." in target:
            raise ValueError(
                f"{where}: {keyword} chỉ nhận tên Page, không phải element: {target!r}"
            )
        page_name, element_key = target, None
    else:
        match = ELEMENT_TARGET.fullmatch(target)
        if not match:
            raise ValueError(
                f"{where}: {keyword} cần Target dạng Page.Element, đang là {target!r}"
            )
        page_name, element_key = match.groups()
    try:
        page_class = load_page_class(page_name)  # chỉ import class, KHÔNG tạo driver
    except TargetError as exc:
        raise ValueError(f"{where}: {exc}") from None
    if element_key is not None:
        if not getattr(page_class, "PAGE_NAME", ""):
            raise ValueError(f"{where}: {page_name} chưa khai báo PAGE_NAME")
        if not get_locator_reader(LOCATOR_FILE).has_locator(
            page_class.PAGE_NAME, element_key
        ):
            raise ValueError(
                f"{where}: element {element_key!r} chưa có trong locators.xlsx "
                f"(Page={page_class.PAGE_NAME!r})"
            )


def _check_cells(where, keyword, row):
    """forbidden: luôn phải trống. required: không được trống (ô placeholder coi là có giá trị trước khi bind)."""
    spec = KEYWORD_SPEC.get(keyword)
    if spec is None:
        return
    for field in ("data", "expected"):
        rule = getattr(spec, field)
        if rule == "forbidden" and row[field]:
            raise ValueError(f"{where}: {keyword} không dùng {field}")
        if rule == "required" and not row[field]:
            hint = "; muốn nhập rỗng hãy ghi <empty>" if keyword == "SetText" else ""
            raise ValueError(f"{where}: {keyword} cần {field}, đang để trống{hint}")


def validate_template(template):
    """Kiểm tra cấu trúc trước binding (keyword/target hợp lệ, step liên tục)."""
    if not isinstance(template, list) or not template:
        raise ValueError("Template không có bước")
    template_id = template[0].get("template_id")
    for number, row in enumerate(template, 1):
        where = f"Template {template_id!r} bước {number}"
        if set(row) != TEMPLATE_FIELDS:
            raise ValueError(f"{where}: sai schema")
        if any(not isinstance(v, str) for v in row.values()):
            raise ValueError(f"{where}: giá trị phải là chuỗi")
        if (
            not template_id
            or row["template_id"] != template_id
            or row["step"] != str(number)
        ):
            raise ValueError(f"{where}: sai template_id hoặc thứ tự step")

        keyword = row["keyword"]
        try:
            REGISTRY.resolve(keyword)  # đúng PascalCase + đã đăng ký
        except (KeyError, TypeError) as exc:
            raise ValueError(f"{where}: {exc.args[0] if exc.args else exc}") from None
        _validate_target(where, keyword, row["target"])

        for field in ("data", "expected"):
            value = row[field]
            if ("{" in value or "}" in value) and not PLACEHOLDER.fullmatch(value):
                raise ValueError(f"{where}: placeholder phải chiếm toàn ô: {value!r}")
        _check_cells(where, keyword, row)

    if template[0]["keyword"] not in START_KEYWORDS:
        raise ValueError(
            f"Template {template_id!r} phải bắt đầu bằng một trong {sorted(START_KEYWORDS)}"
        )
    if not any(r["keyword"].startswith("Verify") for r in template):
        raise ValueError(f"Template {template_id!r} phải có ít nhất một Verify")
    return template


def validate_steps(steps):
    """Kiểm tra GIÁ TRỊ sau binding (lúc này mới biết data/expected thật)."""
    for row in steps:
        _check_cells(f"Case {row['case_id']} step {row['step']}", row["keyword"], row)
    return steps


def bind_template(template, case):
    """Trả list bước MỚI; không sửa template hoặc case. Template đã validate trước đó."""
    if not case.get("case_id") or case.get("template_id") != template[0]["template_id"]:
        raise ValueError("case_id rỗng hoặc template_id không khớp")
    steps = []
    for template_row in template:
        row = {k: v for k, v in template_row.items() if k != "template_id"}
        row["case_id"] = case["case_id"]
        for field in ("data", "expected"):
            match = PLACEHOLDER.fullmatch(row[field])
            if match:
                key = match.group(1)
                if key not in case:
                    raise ValueError(
                        f"Case {case['case_id']}: thiếu cột {key!r} trong test_case"
                    )
                row[field] = case[key]
        steps.append(row)
    return validate_steps(steps)
