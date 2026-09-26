# Interface Specification: Excel ↔ Keyword ↔ Target

## 1. Mục đích

Tài liệu này định nghĩa **hợp đồng giao tiếp** giữa:

```text
Excel Test Case
      ↓
Keyword
      ↓
Target
      ↓
Page Object
      ↓
Locator
      ↓
Selenium WebDriver
```

Mục tiêu là đảm bảo người thiết kế test case và người triển khai framework sử dụng cùng một quy ước.

---

## 2. Cấu trúc một Test Step

Mỗi test step được biểu diễn bằng:

```text
TestCaseID | Step | Keyword | Target | Data | Expected
```

Ví dụ:

| TestCaseID  | Step | Keyword     | Target                   | Data                      | Expected         |
| ----------- | ---: | ----------- | ------------------------ | ------------------------- | ---------------- |
| TC_LOGIN_01 |    1 | NAVIGATE    |                          | https://example.com/login |                  |
| TC_LOGIN_01 |    2 | ENTER_TEXT  | LoginPage.username_field | admin                     |                  |
| TC_LOGIN_01 |    3 | ENTER_TEXT  | LoginPage.password_field | 123456                    |                  |
| TC_LOGIN_01 |    4 | CLICK       | LoginPage.login_button   |                           |                  |
| TC_LOGIN_01 |    5 | VERIFY_TEXT | LoginPage.message        |                           | Login successful |

---

## 3. Quy ước từng trường

### 3.1 TestCaseID

Dùng để xác định một test case.

Quy ước:

```text
<FUNCTION>_<NUMBER>
```

Ví dụ:

```text
LOGIN_01
SEARCH_01
CART_01
```

Các step có cùng `TestCaseID` thuộc cùng một test case.

---

### 3.2 Step

Là thứ tự thực thi trong một test case.

Ví dụ:

```text
1
2
3
4
5
```

Step bắt đầu từ 1 và tăng dần trong cùng TestCaseID.

---

### 3.3 Keyword

Tên keyword phải tồn tại trong Keyword Registry.

Ví dụ:

```VerifyText
CloseBrowser
VerifyElement
VerifyAttribute
```

Không được tự ý tạo keyword mới trong Excel nếu keyword đó chưa được định nghĩa trong Keyword Specification.

---

### 3.4 Target

Target xác định Page Object và element mà keyword thao tác.

Format chính thức:

```text
<PageObject>.<element>
```

Ví dụ:

```text
LoginPage.username_field
LoginPage.password_field
LoginPage.login_button
HomePage.search_box
ProductPage.add_to_cart_button
```

Target không chứa XPath/CSS/ID trực tiếp.

Sai:

```text
//input[@id='username']
#username
button[type='submit']
```

Đúng:

```text
LoginPage.username_field
```

---

## 4. Target Resolution

Khi framework nhận:

```text
Target = LoginPage.username_field
```

nó thực hiện:

```text
LoginPage.username_field
        ↓
Page Object = LoginPage
        ↓
Element key = username_field
        ↓
LoginPage.LOCATORS["username_field"]
        ↓
(By.ID, "username")
        ↓
Selenium WebDriver
```

Target vì vậy là **logical reference**, không phải locator Selenium.

---

## 5. Quy tắc Data

`Data` chứa dữ liệu đầu vào của keyword.

Ví dụ:

```text
ENTER_TEXT
Target = LoginPage.username_field
Data = admin
```

Framework truyền:

```text
admin
```

vào keyword.

### Keyword có Data

| Keyword        | Data     |
| -------------- | -------- |
| `ENTER_TEXT`   | Bắt buộc |
| `NAVIGATE`     | Bắt buộc |
| `CLICK`        | Không    |
| `CLEAR_TEXT`   | Không    |
| `VERIFY_TEXT`  | Không    |
| `VERIFY_ERROR` | Không    |

---

## 6. Quy tắc Expected

`Expected` chỉ được sử dụng cho các bước verification.

Ví dụ:

```text
VERIFY_TEXT
Target = HomePage.page_title
Expected = Welcome
```

hoặc:

```text
VERIFY_ERROR
Target = LoginPage.error_message
Expected = Invalid username or password
```

Các keyword thao tác không cần Expected:

```text
CLICK
ENTER_TEXT
CLEAR_TEXT
NAVIGATE
```

---

## 7. Ma trận Keyword ↔ Target ↔ Data ↔ Expected

| Keyword                  | Target | Data  | Expected |
| ------------------------ | ------ | ----- | -------- |
| `NAVIGATE`               | Không  | Có    | Không    |
| `BACK`                   | Không  | Không | Không    |
| `REFRESH`                | Không  | Không | Không    |
| `ENTER_TEXT`             | Có     | Có    | Không    |
| `CLEAR_TEXT`             | Có     | Không | Không    |
| `CLICK`                  | Có     | Không | Không    |
| `VERIFY_TEXT`            | Có     | Không | Có       |
| `VERIFY_URL`             | Không  | Không | Có       |
| `VERIFY_ELEMENT_VISIBLE` | Có     | Không | Không    |
| `VERIFY_ERROR`           | Có     | Không | Có       |

Quy tắc này giúp tránh việc Excel chứa dữ liệu không cần thiết.

---

## 8. Mapping Keyword → POM

Ví dụ:

```text
Keyword:
    ENTER_TEXT

Target:
    LoginPage.username_field

Data:
    admin
```

Luồng:

```text
Excel
  ↓
KeywordExecutor
  ↓
ENTER_TEXT
  ↓
LoginPage.username_field
  ↓
LoginPage
  ↓
BasePage / Page method
  ↓
LOCATORS["username_field"]
  ↓
(By.ID, "username")
  ↓
Selenium
```

---

## 9. Mapping Verification

Ví dụ:

```text
Keyword = VERIFY_TEXT
Target = LoginPage.message
Expected = Login successful
```

Luồng:

```text
VERIFY_TEXT
     ↓
LoginPage.message
     ↓
POM lấy actual text
     ↓
actual = "Login successful"
     ↓
so sánh với Expected
     ↓
PASS
```

Nếu:

```text
actual != expected
```

thì:

```text
FAIL
```

---

## 10. Target Naming Convention

Tên element phải mô tả ý nghĩa của element, không mô tả locator kỹ thuật.

Nên dùng:

```text
username_field
password_field
login_button
error_message
search_box
product_title
add_to_cart_button
```

Không nên dùng:

```text
id_username
xpath_login_button
css_button_01
input_1
button_2
```

Lý do: locator có thể thay đổi nhưng ý nghĩa nghiệp vụ của element không nhất thiết thay đổi.

---

## 11. Page Object Naming Convention

Tên Page Object:

```text
<PageName>Page
```

Ví dụ:

```text
LoginPage
HomePage
SearchPage
ProductPage
CartPage
```

Target hoàn chỉnh:

```text
LoginPage.username_field
HomePage.search_box
ProductPage.add_to_cart_button
CartPage.checkout_button
```

---

## 12. Quy tắc lỗi interface

Framework phải báo lỗi rõ ràng nếu:

### Keyword không tồn tại

```text
Unknown keyword: ENTER_USERNAME
```

### Target không hợp lệ

```text
Invalid target: LoginPage
Expected format: PageName.elementName
```

### Page Object không tồn tại

```text
Page not found: LoginPage
```

### Element key không tồn tại

```text
Element not found:
LoginPage.username_field
```

### Keyword yêu cầu Data nhưng Data trống

```text
Keyword ENTER_TEXT requires Data
```

### Verification thiếu Expected

```text
Keyword VERIFY_TEXT requires Expected
```

---

## 13. Ví dụ hoàn chỉnh

### Login thành công

| TestCaseID  | Step | Keyword     | Target                   | Data     | Expected |
| ----------- | ---: | ----------- | ------------------------ | -------- | -------- |
| TC_LOGIN_01 |    1 | NAVIGATE    |                          | `/login` |          |
| TC_LOGIN_01 |    2 | ENTER_TEXT  | LoginPage.username_field | admin    |          |
| TC_LOGIN_01 |    3 | ENTER_TEXT  | LoginPage.password_field | 123456   |          |
| TC_LOGIN_01 |    4 | CLICK       | LoginPage.login_button   |          |          |
| TC_LOGIN_01 |    5 | VERIFY_TEXT | HomePage.page_title      |          | Welcome  |

### Login thất bại

| TestCaseID  | Step | Keyword      | Target                   | Data       | Expected                     |
| ----------- | ---: | ------------ | ------------------------ | ---------- | ---------------------------- |
| TC_LOGIN_02 |    1 | NAVIGATE     |                          | `/login`   |                              |
| TC_LOGIN_02 |    2 | ENTER_TEXT   | LoginPage.username_field | wrong_user |                              |
| TC_LOGIN_02 |    3 | ENTER_TEXT   | LoginPage.password_field | wrong_pass |                              |
| TC_LOGIN_02 |    4 | CLICK        | LoginPage.login_button   |            |                              |
| TC_LOGIN_02 |    5 | VERIFY_ERROR | LoginPage.error_message  |            | Invalid username or password |

---

## 14. Nguyên tắc cốt lõi

```text
Excel không biết XPath.
Keyword không biết XPath.
POM biết locator.
Selenium thực thi locator.
```

Cụ thể:

```text
Excel
  ↓
Keyword + Target + Data + Expected
  ↓
Keyword Executor
  ↓
Keyword Library
  ↓
POM
  ↓
Locator
  ↓
Selenium
```

Đây là interface chính thức mà `test_data_spec.md`, `keyword_spec.md` và `pom_design.md` phải tuân theo.
