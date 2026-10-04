# HYBRID BINDING
# Ghép template với MỘT dòng test_case.
# Không mở browser.
#
# Excel sheet:
#   test_steps
#
# Cấu trúc:
#   template_id | step | keyword | target | data | expected
#
# Placeholder:
#   {username}
#   {password}
#   {expected_url}
#
# Chỉ hỗ trợ placeholder chiếm toàn bộ một ô.
# Ví dụ:
#   {username}          -> hợp lệ
#   User: {username}    -> không hợp lệ
#
# Keyword trong Excel KHÔNG phân biệt hoa/thường:
#   navigate
#   Navigate
#   NAVIGATE
#
# Registry vẫn sử dụng tên keyword chuẩn nội bộ.


import re

from config import LOCATOR_FILE
from keywords.keyword_registry import build_default_registry
from keywords.keyword_spec import KEYWORD_SPEC, START_KEYWORDS
from keywords.target_resolver import TargetError, load_page_class
from utils.locator_reader import get_locator_reader

REGISTRY = build_default_registry()


# ============================================================
# CONSTANTS
# ============================================================

TEMPLATE_FIELDS = {
    "template_id",
    "step",
    "keyword",
    "target",
    "data",
    "expected",
}

PLACEHOLDER = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")

ELEMENT_TARGET = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)")


# ============================================================
# CHECK REGISTRY
# ============================================================

assert set(KEYWORD_SPEC) <= set(REGISTRY.names), "KEYWORD_SPEC có keyword chưa đăng ký"


# ============================================================
# KEYWORD NORMALIZATION
# ============================================================


def _build_keyword_aliases():
    """
    Tạo map keyword không phân biệt hoa/thường.

    Ví dụ registry có:
        Navigate
        SetText
        ClickElement
        VerifyUrl

    thì Excel có thể ghi:
        navigate
        Navigate
        NAVIGATE
        setText
        SETTEXT
        verifyUrl

    Tất cả đều được map về keyword chuẩn của registry.
    """

    aliases = {}

    for name in REGISTRY.names:
        key = str(name).strip().lower()

        if key in aliases and aliases[key] != name:
            raise ValueError(
                f"Keyword bị trùng khi không phân biệt hoa/thường: "
                f"{aliases[key]!r} và {name!r}"
            )

        aliases[key] = name

    return aliases


KEYWORD_ALIASES = _build_keyword_aliases()


def _normalize_keyword(keyword):
    """
    Chuẩn hóa keyword từ Excel về tên keyword chuẩn trong Registry.

    Excel:
        navigate
        setText
        clickElement
        verifyUrl

    Có thể map thành:
        Navigate
        SetText
        ClickElement
        VerifyUrl
    """

    if not isinstance(keyword, str):
        raise ValueError(f"Keyword phải là chuỗi, nhận được {type(keyword).__name__}")

    keyword = keyword.strip()

    if not keyword:
        raise ValueError("Keyword không được để trống")

    canonical = KEYWORD_ALIASES.get(keyword.lower())

    if canonical is None:
        raise ValueError(
            f"Keyword không tồn tại: {keyword!r}. "
            f"Keyword hợp lệ: {sorted(REGISTRY.names)}"
        )

    return canonical


# ============================================================
# EMPTY CELL NORMALIZATION
# ============================================================


def _clean_cell(value):
    """
    Chuẩn hóa giá trị đọc từ Excel.

    Excel có thể trả:
        None
        NaN
        " "
        "   "

    thành chuỗi rỗng.
    """

    if value is None:
        return ""

    # Xử lý NaN mà không bắt buộc pandas
    try:
        if value != value:
            return ""
    except Exception:
        pass

    return str(value).strip()


def _normalize_row(row):
    """
    Chuẩn hóa một dòng đọc từ Excel.

    Sau bước này:
        keyword -> keyword chuẩn
        target/data/expected -> chuỗi sạch
    """

    normalized = {key: _clean_cell(row.get(key, "")) for key in TEMPLATE_FIELDS}

    normalized["keyword"] = _normalize_keyword(normalized["keyword"])

    return normalized


# ============================================================
# TARGET VALIDATION
# ============================================================


def _validate_target(where, keyword, target):
    """
    Kiểm tra target theo KEYWORD_SPEC.

    target có thể là:

        ""
        login
        login.username
        login.password
        login.loginButton

    tùy theo cấu hình target của keyword.
    """

    target = _clean_cell(target)

    spec = KEYWORD_SPEC.get(keyword)

    if spec is None:
        return

    kind = spec.target

    # --------------------------------------------------------
    # Keyword không sử dụng Target
    # --------------------------------------------------------

    if kind == "none":
        if target:
            raise ValueError(f"{where}: {keyword} không dùng Target")

        return

    # --------------------------------------------------------
    # Target tùy ý
    # --------------------------------------------------------

    if kind == "any":
        return

    # --------------------------------------------------------
    # Target là Page
    #
    # Ví dụ:
    #   target = login
    # --------------------------------------------------------

    if kind == "page":

        if not target:
            raise ValueError(f"{where}: {keyword} cần tên Page trong Target")

        if "." in target:
            raise ValueError(
                f"{where}: {keyword} chỉ nhận tên Page, "
                f"không phải element: {target!r}"
            )

        page_name = target
        element_key = None

    # --------------------------------------------------------
    # Target là Page.Element
    #
    # Ví dụ:
    #   login.username
    #   login.password
    #   login.loginButton
    # --------------------------------------------------------

    else:

        if not target:
            raise ValueError(f"{where}: {keyword} cần Target dạng Page.Element")

        match = ELEMENT_TARGET.fullmatch(target)

        if not match:
            raise ValueError(
                f"{where}: {keyword} cần Target dạng "
                f"Page.Element, đang là {target!r}"
            )

        page_name, element_key = match.groups()

    # --------------------------------------------------------
    # Load Page class
    #
    # Chỉ import class.
    # KHÔNG tạo browser / driver.
    # --------------------------------------------------------

    try:
        page_class = load_page_class(page_name)

    except TargetError as exc:
        raise ValueError(f"{where}: {exc}") from None

    # --------------------------------------------------------
    # Nếu target là element thì kiểm tra locator
    # --------------------------------------------------------

    if element_key is not None:

        page_name_value = getattr(page_class, "PAGE_NAME", "")

        if not page_name_value:
            raise ValueError(f"{where}: {page_name} chưa khai báo PAGE_NAME")

        locator_reader = get_locator_reader(LOCATOR_FILE)

        if not locator_reader.has_locator(
            page_name_value,
            element_key,
        ):
            raise ValueError(
                f"{where}: element {element_key!r} "
                f"chưa có trong locators.xlsx "
                f"(Page={page_name_value!r})"
            )


# ============================================================
# DATA / EXPECTED VALIDATION
# ============================================================


def _check_cells(where, keyword, row):
    """
    Kiểm tra data và expected dựa trên KEYWORD_SPEC.

    forbidden:
        bắt buộc phải rỗng

    required:
        bắt buộc phải có giá trị
    """

    spec = KEYWORD_SPEC.get(keyword)

    if spec is None:
        return

    for field in ("data", "expected"):

        value = _clean_cell(row.get(field, ""))

        rule = getattr(spec, field)

        # ----------------------------------------------------
        # FORBIDDEN
        # ----------------------------------------------------

        if rule == "forbidden" and value:
            raise ValueError(f"{where}: {keyword} không dùng {field}")

        # ----------------------------------------------------
        # REQUIRED
        # ----------------------------------------------------

        if rule == "required" and not value:

            hint = ""

            if keyword == "SetText":
                hint = "; muốn nhập rỗng hãy ghi <empty>"

            raise ValueError(f"{where}: {keyword} cần {field}, " f"đang để trống{hint}")


# ============================================================
# PLACEHOLDER VALIDATION
# ============================================================


def _validate_placeholder(where, value):
    """
    Placeholder phải chiếm toàn bộ ô.

    Hợp lệ:
        {username}

    Không hợp lệ:
        User: {username}
        {username}_abc
        {username} {password}
        {username.lower()}
    """

    value = _clean_cell(value)

    if not value:
        return

    if "{" in value or "}" in value:

        if not PLACEHOLDER.fullmatch(value):
            raise ValueError(f"{where}: placeholder phải chiếm toàn ô: " f"{value!r}")


# ============================================================
# VALIDATE ONE TEMPLATE
# ============================================================


def validate_template(template):
    """
    Validate MỘT template.

    Ví dụ template:

        LOGIN_VALID
            1 Navigate
            2 SetText
            3 SetText
            4 ClickElement
            5 VerifyUrl
            6 VerifyText

    template phải chứa các dòng của CÙNG một template_id.
    """

    if not isinstance(template, list) or not template:
        raise ValueError("Template không có bước")

    # --------------------------------------------------------
    # Normalize rows
    # --------------------------------------------------------

    template = [_normalize_row(row) for row in template]

    template_id = template[0]["template_id"]

    if not template_id:
        raise ValueError("template_id không được để trống")

    # --------------------------------------------------------
    # Validate từng step
    # --------------------------------------------------------

    for number, row in enumerate(template, 1):

        where = f"Template {template_id!r} " f"bước {number}"

        # Schema
        if set(row) != TEMPLATE_FIELDS:
            raise ValueError(f"{where}: sai schema")

        # template_id
        if row["template_id"] != template_id:
            raise ValueError(f"{where}: template_id không đồng nhất")

        # step
        if row["step"] != str(number):
            raise ValueError(
                f"{where}: step phải là {number}, " f"đang là {row['step']!r}"
            )

        keyword = row["keyword"]

        # ----------------------------------------------------
        # Keyword
        # ----------------------------------------------------

        try:
            REGISTRY.resolve(keyword)

        except (KeyError, TypeError) as exc:
            raise ValueError(
                f"{where}: " f"{exc.args[0] if exc.args else exc}"
            ) from None

        # ----------------------------------------------------
        # Target
        # ----------------------------------------------------

        _validate_target(
            where,
            keyword,
            row["target"],
        )

        # ----------------------------------------------------
        # Placeholder
        # ----------------------------------------------------

        _validate_placeholder(
            f"{where} data",
            row["data"],
        )

        _validate_placeholder(
            f"{where} expected",
            row["expected"],
        )

        # ----------------------------------------------------
        # data / expected
        # ----------------------------------------------------

        _check_cells(
            where,
            keyword,
            row,
        )

    # ========================================================
    # START KEYWORD
    # ========================================================

    start_keyword = template[0]["keyword"]

    # START_KEYWORDS có thể chứa keyword chuẩn.
    # Chuẩn hóa để so sánh không phụ thuộc hoa/thường.

    normalized_start_keywords = {
        _normalize_keyword(keyword) for keyword in START_KEYWORDS
    }

    if start_keyword not in normalized_start_keywords:

        raise ValueError(
            f"Template {template_id!r} phải bắt đầu "
            f"bằng một trong "
            f"{sorted(normalized_start_keywords)}"
        )

    # ========================================================
    # VERIFY
    # ========================================================

    has_verify = any(row["keyword"].lower().startswith("verify") for row in template)

    if not has_verify:
        raise ValueError(f"Template {template_id!r} phải có ít nhất một Verify")

    return template


# ============================================================
# VALIDATE ALL TEMPLATES FROM test_steps
# ============================================================


def validate_templates(rows):
    """
    Validate toàn bộ sheet test_steps.

    Sheet có thể chứa:

        LOGIN_VALID
        LOGIN_INVALID_CREDENTIALS
        LOGIN_EMPTY_FIELD
        LOGIN_MAX_LENGTH

    Hàm sẽ tự nhóm theo template_id.

    Kết quả:

        {
            "LOGIN_VALID": [...],
            "LOGIN_INVALID_CREDENTIALS": [...],
            "LOGIN_EMPTY_FIELD": [...],
            "LOGIN_MAX_LENGTH": [...]
        }
    """

    if not isinstance(rows, list) or not rows:
        raise ValueError("Sheet test_steps không có dữ liệu")

    groups = {}

    for index, raw_row in enumerate(rows, 2):

        row = _normalize_row(raw_row)

        template_id = row["template_id"]

        if not template_id:
            raise ValueError(
                f"test_steps dòng {index}: " f"template_id không được để trống"
            )

        groups.setdefault(template_id, []).append(row)

    validated = {}

    for template_id, template_rows in groups.items():

        validated[template_id] = validate_template(template_rows)

    return validated


# ============================================================
# VALIDATE BOUND STEPS
# ============================================================


def validate_steps(steps):
    """
    Kiểm tra GIÁ TRỊ sau binding.

    Lúc này:

        {username}

    đã trở thành:

        student01
    """

    for row in steps:

        _check_cells(
            f"Case {row['case_id']} " f"step {row['step']}",
            row["keyword"],
            row,
        )

    return steps


# ============================================================
# BIND TEMPLATE + ONE TEST CASE
# ============================================================


def bind_template(template, case):
    """
    Ghép MỘT template với MỘT dòng test_case.

    Không sửa template.
    Không sửa case.
    Không mở browser.

    Ví dụ:

        template:

            data = "{username}"

        case:

            username = "student01"

        kết quả:

            data = "student01"
    """

    if not isinstance(template, list) or not template:
        raise ValueError("Template không có bước")

    if not case.get("case_id"):
        raise ValueError("case_id không được để trống")

    if case.get("template_id") != template[0]["template_id"]:
        raise ValueError("case_id rỗng hoặc template_id không khớp")

    steps = []

    for template_row in template:

        row = {
            key: value for key, value in template_row.items() if key != "template_id"
        }

        row["case_id"] = case["case_id"]

        # ----------------------------------------------------
        # Bind data / expected
        # ----------------------------------------------------

        for field in ("data", "expected"):

            match = PLACEHOLDER.fullmatch(row[field])

            if match:

                key = match.group(1)

                if key not in case:

                    raise ValueError(
                        f"Case {case['case_id']}: "
                        f"thiếu cột {key!r} "
                        f"trong test_case"
                    )

                row[field] = _clean_cell(case[key])

        steps.append(row)

    return validate_steps(steps)
