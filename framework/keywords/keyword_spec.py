# Bảng mô tả "hợp đồng" của từng keyword, dùng để validate Excel TRƯỚC khi mở browser.
# Thêm keyword mới = thêm 1 dòng ở đây, không phải sửa logic validate.
#
# target   : "page"    -> LoginPage
#            "element" -> LoginPage.Username
#            "none"    -> cột target phải trống
#            "any"     -> không kiểm tra
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
    "Navigate": Spec(target="page", data="forbidden", expected="forbidden"),
    "SetText": Spec(target="element", data="required"),  # rỗng thì ghi <empty>
    "ClickElement": Spec(target="element"),
    "VerifyUrl": Spec(expected="required"),
    "VerifyText": Spec(target="element", expected="required"),
    "VerifyFieldState": Spec(target="element", expected="required"),
    "VerifyAttribute": Spec(target="element", data="required"),  # data = tên attribute
    # Keyword chưa liệt kê (Login, AddToCart, ...) vẫn chạy, chỉ chưa được kiểm tra sớm.
}

# Keyword được phép đứng đầu template.
START_KEYWORDS = {"Navigate"}
