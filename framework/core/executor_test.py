# TEST EXECUTOR: điều phối ở tầng TESTCASE - kiểm tra schema chung, thứ tự step,
# case_id nhất quán, sau đó duyệt từng step và giao cho KeywordExecutor xử lý.

from .keyword_executor import KeywordExecutor

FIELDS = {"case_id", "step", "keyword", "target", "data", "expected"}


class TestExecutor:
    def __init__(self, driver):
        self.driver = driver
        self.keyword_executor = KeywordExecutor(driver)

    def validate_steps(self, steps):
        """Kiểm tra schema + tính nhất quán của cả testcase (không xét luật riêng keyword)."""
        if not isinstance(steps, list) or not steps:
            raise ValueError("Kịch bản không có bước")

        case_id = steps[0].get("case_id") if isinstance(steps[0], dict) else None

        for index, row in enumerate(steps, 1):
            if not isinstance(row, dict) or set(row) != FIELDS:
                raise ValueError(f"Bước {index}: sai schema")
            if any(not isinstance(value, str) for value in row.values()):
                raise ValueError(f"Bước {index}: dữ liệu phải là chuỗi")
            if not case_id or row["case_id"] != case_id or row["step"] != str(index):
                raise ValueError(f"Bước {index}: sai case_id hoặc thứ tự step")

            # Luật riêng của từng keyword (target/data/expected hợp lệ...)
            # được uỷ quyền hoàn toàn cho KeywordExecutor.
            self.keyword_executor.validate_step(row, index)

        if steps[0]["keyword"] != "navigate":
            raise ValueError("Bước đầu phải navigate")
        if not any(row["keyword"].startswith("verify") for row in steps):
            raise ValueError("Kịch bản cần ít nhất một bước verify")

        return steps

    def run(self, steps):
        """Validate cả testcase, sau đó duyệt từng step và gọi KeywordExecutor thực thi."""
        self.validate_steps(steps)

        for row in steps:
            # In mã ca/bước để debug; không nuốt lỗi rồi báo PASS.
            print(
                f"{row['case_id']} | step {row['step']} | {row['keyword']} | {row['target']}"
            )
            try:
                self.keyword_executor.execute(row)
            except Exception as error:
                # Bổ sung ngữ cảnh rồi ném lại cùng exception, giữ traceback gốc.
                error.add_note(
                    f"Case {row['case_id']}, step {row['step']}, keyword {row['keyword']}"
                )
                raise

        return "PASS"
