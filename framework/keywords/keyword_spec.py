# Bảng mô tả "hợp đồng" của từng keyword, dùng để validate Excel TRƯỚC khi mở browser.
# Thêm keyword mới = thêm 1 dòng ở đây, không phải sửa logic validate.
#
# target   : "page"    -> LoginPage
#            "element" -> LoginPage.Username
#            "none"    -> cột target phải trống
#            "any"     -> không kiểm tra
#            "optional_element" -> để trống hoặc Page.Element
# data / expected:
#            "required"  -> không được trống (sau khi bind)
#            "forbidden" -> phải trống
#            "optional"  -> không kiểm tra
from dataclasses import dataclass


@dataclass(frozen=True)
class Spec:
    target: str = "any"
    data: str = "optional"
    expected: str = "optional"


KEYWORD_SPEC = {
    "Navigate": Spec(target="none", data="required", expected="forbidden"),
    "SetText": Spec(target="element", data="required", expected="forbidden"),
    "ClearText": Spec(target="element", data="forbidden", expected="forbidden"),
    "ClickElement": Spec(target="element", data="forbidden", expected="forbidden"),
    "ClickOutside": Spec(target="page", data="forbidden", expected="forbidden"),
    "SelectOption": Spec(target="element", data="required", expected="forbidden"),
    "VerifyUrl": Spec(target="none", data="forbidden", expected="required"),
    "VerifyAlert": Spec(target="none", data="forbidden", expected="required"),
    "VerifyText": Spec(target="element", data="forbidden", expected="required"),
    "VerifyTextContains": Spec(target="element", data="forbidden", expected="required"),
    "VerifyFieldState": Spec(target="element", data="forbidden", expected="required"),
    "VerifyAttribute": Spec(target="element", data="required", expected="required"),
    "VerifyElement": Spec(target="element", data="forbidden"),
    "VerifyElementCount": Spec(target="element", data="forbidden", expected="required"),
    # Existing workbooks may fill Expected even though this handler ignores it.
    "VerifyElementNotExist": Spec(target="element", data="forbidden"),
    "VerifyCalculation": Spec(
        target="optional_element", data="required", expected="required"
    ),
    "VerifyKeyword": Spec(data="required"),
    "VerifyDataMatch": Spec(target="element", data="forbidden", expected="required"),
    "Login": Spec(target="page", expected="forbidden"),
    "AddToCart": Spec(target="page", data="required", expected="forbidden"),
    "SetProductOutOfStock": Spec(target="page", data="forbidden", expected="forbidden"),
}

# Keyword được phép đứng đầu template.
START_KEYWORDS = {"Navigate"}
