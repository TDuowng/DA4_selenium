# Test Data Spec (Excel) — Design Doc

## 1. Mục tiêu & phạm vi

- Doc này thiết kế cấu trúc file Excel dùng làm Test Data cho Keyword Layer
- Không ảnh hưởng đến Config Layer, Locator trong Page Object.

## 2. Cấu trúc file & sheet

data/excel/
├── login_test.xlsx
├── search_test.xlsx
└── form_test.xlsx

Mỗi file gồm 2 sheet:

- `TestSteps`: các bước test case
- `KeywordList`: danh sách keyword hợp lệ (dùng cho dropdown validation)

## 3. Sheet "TestSteps" — cấu trúc cột

| Cột      | Kiểu   | Bắt buộc | Mô tả                                     |
| -------- | ------ | -------- | ----------------------------------------- |
| TestCase | text   | có       | Tên/ID case, lặp lại ở mọi step cùng case |
| Step     | number | có       | Số thứ tự bước trong case                 |
| Keyword  | text   | có       | Tên keyword, phải khớp KeywordList        |
| Object   | text   | không    | Key locator, tra trong Page Object        |
| Value    | text   | không    | Dữ liệu nhập hoặc giá trị kỳ vọng         |
| Expected | text   | không    | Kết quả mong đợi (dùng cho VerifyText...) |
| Note     | text   | không    | Ghi chú cho người đọc                     |

### Ví dụ dữ liệu

| TestCase      | Step | Keyword      | Object          | Value               | Expected        | Note |
| ------------- | ---- | ------------ | --------------- | ------------------- | --------------- | ---- |
| login_success | 1    | OpenBrowser  |                 | https://example.com |                 |      |
| login_success | 2    | InputText    | username_field  | admin               |                 |      |
| login_success | 3    | InputText    | password_field  | 123456              |                 |      |
| login_success | 4    | ClickElement | login_button    |                     |                 |      |
| login_success | 5    | VerifyText   | welcome_message |                     | Xin chào, admin |      |

## 4. Sheet "KeywordList"

| Keyword      |
| ------------ |
| OpenBrowser  |
| InputText    |
| ClickElement |
| VerifyText   |
| ...          |

Dùng Data Validation (Excel) trỏ cột `Keyword` ở sheet TestSteps tới
danh sách này, để người điền không gõ sai tên keyword.

## 5. Quy ước nhóm test case

- Mỗi step là 1 dòng, `TestCase` lặp lại ở mọi dòng cùng case
  (không merge cell) — giúp code Python đọc bằng pandas dễ nhóm theo
  `groupby("TestCase")`.

## 6. Loader đọc Excel

```python
# utils/excel_loader.py
import pandas as pd
from typing import Dict, List

def load_excel_test_steps(path: str) -> Dict[str, List[dict]]:
    df = pd.read_excel(path, sheet_name="TestSteps")
    df = df.sort_values(["TestCase", "Step"])
    grouped = {}
    for case_name, group in df.groupby("TestCase"):
        grouped[case_name] = group.to_dict(orient="records")
    return grouped
```

```python
# tests/test_login_excel.py
from utils.excel_loader import load_excel_test_steps
from keywords.engine import execute_keyword

test_cases = load_excel_test_steps("data/excel/login_test.xlsx")

import pytest
@pytest.mark.parametrize("case_name", test_cases.keys())
def test_login_from_excel(case_name):
    for step in test_cases[case_name]:
        execute_keyword(step["Step"], step["Keyword"], step["Object"], step["Value"])
```

## 7. Giới hạn & việc không làm (Out of scope)

- Không hỗ trợ merge cell cho `TestCase`.
- Không validate kiểu dữ liệu tự động ngoài Excel Data Validation
  (không dùng thư viện schema riêng cho Excel).

## 8. Quy ước & checklist review

- [ ] Mọi giá trị cột Keyword đều có trong sheet KeywordList
- [ ] Mọi TestCase có ít nhất 1 step VerifyText/VerifyElementVisible để có assertion
- [ ] File Excel đặt trong `data/excel/`, tên file khớp tên module test
- [ ] Đã chạy thử loader + execute_keyword() với ít nhất 1 file mẫu trước khi merge
