# Data Layer & Page Object Layer — Design Doc

## 1. Mục tiêu & phạm vi

Doc này mô tả thiết kế chi tiết của **Data Layer** và **Page Object Layer**
— hai thành phần thuộc kiến trúc tổng thể ở Hình 3-1. Phạm vi:

- Cách tổ chức dữ liệu test (định dạng, schema, loader).
- Cách tổ chức Page Object (BasePage, locator, action method).
- Không đề cập Configuration Layer, Utility Layer chi tiết (đã có ở
  các mục khác), Keyword Layer (xem `docs/keyword_design.md`).

## 2. Vị trí trong kiến trúc tổng thể

- **Test Layer** gọi trực tiếp **Data Layer** (lấy dữ liệu đầu vào) và
  **Page Object Layer** (thao tác UI) — không đi qua trung gian.
- **Page Object Layer** nhận đối tượng `driver` (WebDriver) qua constructor,
  do Utility Layer (Driver Factory) khởi tạo và Test Layer truyền vào
  qua fixture.
- **Data Layer** không phụ thuộc Selenium — chỉ đọc/parse file, có thể
  test độc lập không cần trình duyệt.

Test Layer
├──> Data Layer (lấy dữ liệu)
└──> Page Object ──> WebDriver ──> Web Application

## 3. Data Layer

### 3.1 Định dạng & cấu trúc thư mục

Chọn nhiều kiểu định dạng như .json, .csv, .sqlite

data/
├── login_data.json
├── login_data.csv
├── login_data.sqlite
├── search_data.json
└── form_data.json
...

### 3.2 Data Model

Dùng `dataclass` để dữ liệu có kiểu rõ ràng, IDE gợi ý được field,
tránh gõ sai key như khi dùng dict thô.

```python
# models/login_data.py
from dataclasses import dataclass

@dataclass
class LoginData:
    case_name: str
    username: str
    password: str
    expected_result: str      # "success" | "fail"
    expected_message: str
```

### 3.3 Data Reader / Provider

Reader chỉ có 1 việc: đọc file, map sang list dataclass. Không chứa
logic Selenium, không phụ thuộc Page Object.

```python
# utils/data_reader.py
import json
from pathlib import Path
from typing import List
from models.login_data import LoginData

def load_login_data(path: str = "data/login_data.json") -> List[LoginData]:
    file_path = Path(path)
    with file_path.open(encoding="utf-8") as f:
        raw = json.load(f)
    return [LoginData(**item) for item in raw]
```

`login_data.json` mẫu:

```json
[
  {
    "case_name": "login_success",
    "username": "admin",
    "password": "123456",
    "expected_result": "success",
    "expected_message": "Xin chào, admin"
  },
  {
    "case_name": "login_wrong_password",
    "username": "admin",
    "password": "wrongpass",
    "expected_result": "fail",
    "expected_message": "Sai tên đăng nhập hoặc mật khẩu"
  }
]
```

### 3.4 Ví dụ dùng trong test

```python
# tests/test_login.py
import pytest
from utils.data_loader import load_login_data
from pages.login_page import LoginPage

@pytest.mark.parametrize("data", load_login_data(), ids=lambda d: d.case_name)
def test_login(driver, data):
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(data.username, data.password)

    if data.expected_result == "success":
        assert login_page.get_welcome_message() == data.expected_message
    else:
        assert login_page.get_error_message() == data.expected_message
```

## 4. Page Object Layer

### 4.1 BasePage

Chứa các hành động Selenium dùng chung, luôn kèm **explicit wait** —
không dùng `implicit_wait` rải rác để tránh flaky test.

```python
# pages/base_page.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

DEFAULT_TIMEOUT = 10

class BasePage:
    def __init__(self, driver):
        self.driver = driver

    def open_browser(self, url: str):
        self.driver.get(url)

    def close_browser(self):
        self.driver.quit()

    def _wait(self, timeout: int = DEFAULT_TIMEOUT) -> WebDriverWait:
        return WebDriverWait(self.driver, timeout)

    def find(self, locator: tuple):
        return self._wait().until(EC.presence_of_element_located(locator))

    def wait_for_visible(self, locator: tuple):
        return self._wait().until(EC.visibility_of_element_located(locator))

    def click(self, locator: tuple):
        self.wait_for_visible(locator).click()

    def type_text(self, locator: tuple, value: str):
        element = self.wait_for_visible(locator)
        element.clear()
        element.send_keys(value)

    def select_option(self, locator: tuple, value: str):
        from selenium.webdriver.support.ui import Select
        Select(self.find(locator)).select_by_visible_text(value)

    def check(self, locator: tuple):
        element = self.wait_for_visible(locator)
        if not element.is_selected():
            element.click()

    def get_text(self, locator: tuple) -> str:
        return self.wait_for_visible(locator).text

    def assert_text_equals(self, locator: tuple, expected: str):
        actual = self.get_text(locator)
        assert actual == expected, f"Expected '{expected}' but got '{actual}'"

    def assert_visible(self, locator: tuple):
        assert self.wait_for_visible(locator).is_displayed()
```

### 4.2 Quy ước locator

Locator được tách riêng thành dict `LOCATORS` ngay trong file Page
(không tách file `.py` riêng, tránh phải mở 2 file khi maintain) —
key là tên ngắn gọn theo ý nghĩa nghiệp vụ, value là tuple `(By, string)`.

```python
LOCATORS = {
    "username_field": (By.ID, "username"),
    "password_field": (By.ID, "password"),
    "login_button":   (By.CSS_SELECTOR, "button[type='submit']"),
}
```

### 4.3 Quy ước action method

- Tên method theo **hành vi nghiệp vụ** (`login`, `search`), không theo
  hành động Selenium (`click_button_1`) — vì test case gọi method này
  cần đọc hiểu ý nghĩa, không cần biết chi tiết implement.
- Method business-level luôn trả về `None` hoặc dữ liệu cần assert
  (không trả về `WebElement` ra ngoài Page Object).
- Mỗi Page kế thừa `BasePage`, không kế thừa lẫn nhau giữa các Page

### 4.4 Ví dụ: LoginPage

```python
# pages/login_page.py
from selenium.webdriver.common.by import By
from pages.base_page import BasePage

class LoginPage(BasePage):
    URL = "https://example.com/login"

    LOCATORS = {
        "username_field": (By.ID, "username"),
        "password_field": (By.ID, "password"),
        "login_button":   (By.CSS_SELECTOR, "button[type='submit']"),
        "welcome_message": (By.CSS_SELECTOR, ".welcome-msg"),
        "error_message":   (By.CSS_SELECTOR, ".error-msg"),
    }

    def open(self):
        self.open_browser(self.URL)

    def login(self, username: str, password: str):
        self.type_text(self.LOCATORS["username_field"], username)
        self.type_text(self.LOCATORS["password_field"], password)
        self.click(self.LOCATORS["login_button"])

    def get_welcome_message(self) -> str:
        return self.get_text(self.LOCATORS["welcome_message"])

    def get_error_message(self) -> str:
        return self.get_text(self.LOCATORS["error_message"])
```

## 5. Sơ đồ tương tác Data ↔ POM ↔ Test Layer

test_login.py
│
├── load_login_data() ──> [LoginData, LoginData, ...]
│
└── for each LoginData:
LoginPage(driver).login(username, password)
│
└── BasePage.type_text() / click()
│
└── Selenium WebDriver ──> Browser

## 6. Quy ước coding & checklist review

- [ ] Mọi Page kế thừa `BasePage`, không viết `WebDriverWait` trực tiếp trong Page.
- [ ] `LOCATORS` khai báo dạng dict, key là tên nghiệp vụ, không dùng chuỗi locator rời rạc trong code.
- [ ] Action method trả kết quả để assert, không trả `WebElement`.
- [ ] Data Loader không import Selenium — giữ Data Layer độc lập, test được riêng.
- [ ] Mỗi file data (`*.json`) có ít nhất 1 case "success" và 1 case "fail".
- [ ] Đặt tên `case_name` mô tả rõ tình huống, dùng làm `ids=` trong `parametrize` để log dễ đọc.
