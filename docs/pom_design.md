# POM Design

## 1. Mục đích

POM tách biệt locator/UI detail, thao tác trên trang, logic điều phối test và Keyword Layer.

Mỗi trang/UI component chính được biểu diễn bởi một Page Object.

## 2. Nguyên tắc POM

- Locator thuộc Page Object.
- Không có `locators.py`.
- Page Object nhận WebDriver từ bên ngoài.
- Page Object không tự khởi tạo hoặc quit browser.
- Page Object không điều phối test flow.

Ví dụ:

```text
LoginPage
HomePage
SearchPage
ProductPage
CartPage
```

## 3. BasePage

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

Browser lifecycle không thuộc BasePage.

## 4. Locator Convention

Locator khai báo trực tiếp trong Page Object bằng `LOCATORS`:

```python
class LoginPage(BasePage):
    LOCATORS = {
        "username_field": (By.ID, "username"),
        "password_field": (By.ID, "password"),
        "login_button": (By.CSS_SELECTOR, "button[type='submit']"),
        "error_message": (By.CSS_SELECTOR, ".error-message"),
    }
```

Không có file `locators.py`.

## 5. Quy tắc đặt tên element

### Nên dùng

```text
username_field
password_field
login_button
error_message
search_box
product_title
add_to_cart_button
```

### Không nên dùng

```text
xpath_01
id_username
button_1
element_2
css_selector_login
```

## 6. Page Object đặc thù

Page Object có thể chứa UI behavior đặc thù khi cần, nhưng không quản lý test flow.

Generic operation nên đi qua BasePage:

```text
SetText
  ↓
LoginPage.username_field
  ↓
BasePage.enter_text()
```

## 7. Mapping Keyword → POM

```text
ClickElement
  ↓
ProductPage.add_to_cart_button
  ↓
ProductPage.LOCATORS["add_to_cart_button"]
  ↓
BasePage.click()
```

Keyword không chứa locator.

## 8. Target Convention

```text
<PageObject>.<element>
```

Ví dụ:

```text
LoginPage.username_field
LoginPage.password_field
LoginPage.login_button
LoginPage.error_message
```

## 9. Target Resolution

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
WebDriver
```

## 10. WebDriverWait

Ưu tiên explicit wait và condition phù hợp. Không rải `time.sleep()` khi có thể dùng wait.

## 11. Page Object không quản lý Test Flow

Không dùng kiến trúc:

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

## 12. Driver Injection

WebDriver được tạo bởi:

```text
DriverManager / pytest fixture
```

và truyền xuống context/POM.

Page Object không gọi:

```python
webdriver.Chrome()
```

và không `quit()` driver.

## 13. Locator Maintenance

Khi locator thay đổi, chỉ cập nhật `LOCATORS` trong Page Object.

Excel vẫn giữ:

```text
LoginPage.username_field
```

Keyword vẫn giữ:

```text
SetText
```

## 14. Phân trách nhiệm

| Thành phần | Trách nhiệm |
|---|---|
| Excel | TestCaseID, Step, Keyword, Target, Data, Expected |
| Data Layer | Đọc/chuẩn hóa Excel |
| TestExecutor | Điều phối test case |
| KeywordExecutor | Thực thi keyword |
| KeywordRegistry | Resolve keyword → handler |
| Keyword | Action/verification theo contract |
| Page Object | Locator + UI abstraction |
| BasePage | Selenium operations dùng chung |
| DriverManager | WebDriver lifecycle |

## 15. Quy tắc không được vi phạm

1. Không có locator trong Excel.
2. Không có `locators.py`.
3. Không khởi tạo browser trong Page Object.
4. Không đóng browser trong Page Object.
5. Không để Test Layer gọi POM trực tiếp.
6. Không để Keyword Executor chứa locator website.
7. Không để Page Object điều phối test flow.

## 16. Cấu trúc thư mục

```text
pages/
├── base_page.py
├── login_page.py
├── home_page.py
├── search_page.py
├── product_page.py
└── cart_page.py
```

## 17. Tiêu chí hoàn thành

- [ ] Locator nằm trong Page Object.
- [ ] Không có `locators.py`.
- [ ] BasePage chứa thao tác Selenium dùng chung.
- [ ] Page Object nhận driver từ bên ngoài.
- [ ] Browser lifecycle do DriverManager/pytest fixture quản lý.
- [ ] Target là logical reference.
- [ ] Test flow nằm ở Core Executor.
- [ ] Keyword Layer giao tiếp với POM qua target/handler contract.
