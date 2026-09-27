# KEYWORD EXECUTOR: nhận 1 keyword (target, data, expected) -> validate theo
# đúng "luật" của riêng keyword đó -> tìm trong Keyword Registry -> gọi thực thi.
# KHÔNG biết gì về testcase, thứ tự step, hay case_id -> đó là việc của TestExecutor.

import math
from keywords.common_keywords import CommonKeywords
from keywords.login_keywords import LoginKeywords
from keywords.cart_keywords import CartKeywords
from keywords.keyword_registry import registry  
from config import URLS


class KeywordExecutor:
    def __init__(self, driver):
        self.libraries = {
            "common": CommonKeywords(driver),
            "login": LoginKeywords(driver),
            "cart": CartKeywords(driver)
        }

    
    def _lookup(self, keyword, index):
        """
        Điểm DUY NHẤT gọi vào Keyword Registry.
        Nếu sau này bạn đổi format registry (tuple -> object, đổi tên field...),
        chỉ cần sửa ở đây, không phải sửa validate_step()/execute().
        """
        try:
            return registry.resolve(keyword)  # kỳ vọng: (method_name, targets, required)
        except KeyError as error:
            raise ValueError(f"Bước {index}: keyword chưa khai báo: {keyword}") from error

    def validate_step(self, row, index):
        """
        Kiểm tra tính hợp lệ của 1 step, dựa trên "luật" riêng của keyword đó
        (target hợp lệ, có cần data/expected không, kiểu dữ liệu expected...).
        Không kiểm tra thứ tự step hay case_id -> thuộc về TestExecutor.
        """
        keyword = row["keyword"]
        method_name, targets, required = self._lookup(keyword, index)

        if row["target"] not in targets or any(not row[field] for field in required):
            raise ValueError(f"Bước {index}: target/data/expected không hợp lệ")

        # Không âm thầm bỏ qua expected nhập nhầm vào keyword không xác minh.
        if not keyword.startswith("verify") and row["expected"]:
            raise ValueError(f"Bước {index}: keyword này không nhận expected")

        if keyword not in {"navigate", "setText"} and row["data"]:
            raise ValueError(f"Bước {index}: keyword này không nhận data")

        if keyword == "navigate" and row["data"] not in URLS:
            raise ValueError(f"Bước {index}: URL alias chưa khai báo")

        if keyword == "verifyBmiValue":
            self._validate_bmi_expected(row["expected"], index)

    def _validate_bmi_expected(self, expected, index):
        try:
            value = float(expected)
        except ValueError as error:
            raise ValueError(f"Bước {index}: expected BMI phải là số") from error
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f"Bước {index}: expected BMI phải hữu hạn và dương")

    def execute(self, row):
        source, method_name, _, _ = registry.resolve(row["keyword"])
        library = self.libraries[source]
        return getattr(library, method_name)(row["target"], row["data"], row["expected"])