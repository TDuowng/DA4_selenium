# Data Layer & Page Object Layer — Design Doc

## 1. Mục tiêu & phạm vi

Doc này mô tả Data Layer và Page Object Layer trong kiến trúc framework.

- Excel là nguồn test data chính.
- Reader chỉ đọc/chuẩn hóa test step.
- Page Object quản lý locator và UI abstraction.
- Không có nhánh Test Layer gọi trực tiếp Page Object.

## 2. Vị trí trong kiến trúc

```text
Excel
  ↓
Excel Reader / Data Layer
  ↓
TestExecutor
  ↓
KeywordExecutor
  ↓
KeywordRegistry.resolve()
  ↓
Keyword Implementation
  ↓
Page Object
  ↓
BasePage
  ↓
Selenium WebDriver
```

## 3. Data Layer

### 3.1 Định dạng

```text
data/
└── test_cases.xlsx
```

Schema:

| TestCaseID | Step | Keyword | Target | Data | Expected |
|---|---:|---|---|---|---|
| TC_LOGIN_01 | 1 | Navigate | LoginPage | | |
| TC_LOGIN_01 | 2 | SetText | LoginPage.username_field | admin | |
| TC_LOGIN_01 | 3 | SetText | LoginPage.password_field | 123456 | |
| TC_LOGIN_01 | 4 | ClickElement | LoginPage.login_button | | |
| TC_LOGIN_01 | 5 | VerifyText | LoginPage.message | | Login successful |

Không dùng JSON/CSV/SQLite làm nguồn test case chính.

### 3.2 Excel Reader

Reader có trách nhiệm:

1. Mở workbook.
2. Đọc header.
3. Chuẩn hóa cell trống.
4. Tạo step records.
5. Group theo `TestCaseID`.
6. Sắp xếp theo `Step`.

Reader không thực thi keyword và không thao tác browser.

## 4. Page Object Layer

### 4.1 BasePage

File:

```text
pages/base_page.py
```

Method dùng chung:

| Method | Mục đích |
|---|---|
| `click()` | Click element |
| `enter_text()` | Nhập text |
| `clear()` | Xóa nội dung |
| `get_text()` | Lấy text |
| `is_visible()` | Kiểm tra hiển thị |
| `wait_for_element()` | Explicit wait |
| `get_current_url()` | Lấy URL |

Browser không được mở/đóng bởi BasePage.

### 4.2 Locator

Không có `locators.py`.

Locator nằm trực tiếp trong Page Object:

```python
class LoginPage(BasePage):
    LOCATORS = {
        "username_field": (By.ID, "username"),
        "password_field": (By.ID, "password"),
        "login_button": (By.CSS_SELECTOR, "button[type='submit']"),
        "message": (By.CSS_SELECTOR, ".message"),
    }
```

### 4.3 Action method

Page Object có thể chứa behavior đặc thù UI khi cần, nhưng không quản lý test flow.

Generic keyword nên đi qua BasePage:

```text
SetText
  ↓
LoginPage.username_field
  ↓
BasePage.enter_text()
```

## 5. Target Resolution

Format:

```text
<PageObject>.<element>
```

Resolution:

```text
Target
 ↓
Page Object
 ↓
LOCATORS[element]
 ↓
(By, value)
 ↓
BasePage
 ↓
Selenium
```

## 6. Phân tách trách nhiệm

```text
Data Layer → đọc Excel
TestExecutor → điều phối test case
KeywordExecutor → thực thi keyword
Registry → resolve keyword
POM → locator + UI abstraction
BasePage → Selenium operations dùng chung
DriverManager → browser lifecycle
```

## 7. Page Object không quản lý Test Flow

Không thiết kế pipeline:

```text
Test Layer → POM
```

Pipeline chính thức:

```text
Test Layer
 ↓
TestExecutor
 ↓
KeywordExecutor
 ↓
KeywordRegistry.resolve()
 ↓
Keyword
 ↓
POM
```

## 8. WebDriverWait

BasePage/POM ưu tiên explicit wait và condition phù hợp; không rải `time.sleep()` khi có thể dùng wait.

## 9. Quy tắc coding

- Locator thuộc Page Object.
- Không có `locators.py`.
- Page Object nhận driver từ bên ngoài.
- Page Object không tạo/quit WebDriver.
- Không đọc Excel trong Page Object.
- Không có locator Selenium trong Excel.
- Test flow nằm ở Core Executor.

## 10. Cấu trúc thư mục

```text
framework/
├── core/
│   ├── driver_manager.py
│   ├── test_executor.py
│   ├── keyword_executor.py
│   └── test_context.py
├── keywords/
│   ├── keyword_registry.py
│   └── ...
├── pages/
│   ├── base_page.py
│   ├── login_page.py
│   ├── home_page.py
│   ├── search_page.py
│   ├── product_page.py
│   └── cart_page.py
├── data/
│   └── test_cases.xlsx
└── tests/
    └── ...
```
