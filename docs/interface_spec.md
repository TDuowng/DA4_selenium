# Interface Specification: Excel ↔ Keyword ↔ Target

## 1. Mục đích

Định nghĩa hợp đồng giao tiếp giữa Excel Test Case, Keyword Layer và POM.

```text
Excel
 ↓
TestExecutor
 ↓
KeywordExecutor
 ↓
KeywordRegistry.resolve()
 ↓
Keyword
 ↓
Target
 ↓
Page Object
 ↓
LOCATORS
 ↓
Selenium
```

## 2. Cấu trúc một Test Step

```text
TestCaseID | Step | Keyword | Target | Data | Expected
```

Ví dụ:

| TestCaseID | Step | Keyword | Target | Data | Expected |
|---|---:|---|---|---|---|
| TC_LOGIN_01 | 1 | Navigate | LoginPage | | |
| TC_LOGIN_01 | 2 | SetText | LoginPage.username_field | admin | |
| TC_LOGIN_01 | 3 | SetText | LoginPage.password_field | 123456 | |
| TC_LOGIN_01 | 4 | ClickElement | LoginPage.login_button | | |
| TC_LOGIN_01 | 5 | VerifyText | LoginPage.message | | Login successful |

Browser lifecycle không nằm trong bảng step.

## 3. Quy ước trường

### 3.1 TestCaseID

Format:

```text
TC_<FUNCTION>_<NUMBER>
```

### 3.2 Step

Số thứ tự thực thi, bắt đầu từ 1.

### 3.3 Keyword

- PascalCase.
- Phải tồn tại trong Keyword Specification.
- Phải được đăng ký trong Registry.
- Không chứa locator.

### 3.4 Target

Logical reference:

```text
<PageObject>.<element>
```

Ví dụ:

```text
LoginPage.username_field
SearchPage.input
ProductPage.name
```

Không dùng XPath/CSS/ID trực tiếp.

## 4. Target Resolution

```text
LoginPage.username_field
        ↓
LoginPage
        ↓
LoginPage.LOCATORS["username_field"]
        ↓
(By.ID, "username")
        ↓
Selenium
```

Không có file locator riêng.

## 5. Quy tắc Data

Nguồn test case là Excel.

Các keyword có Data theo contract hiện tại gồm:

- `SetText`
- `SelectOption`
- Các keyword khác chỉ có Data khi contract của keyword đó quy định.

`Navigate` dùng page key/target; URL/base URL thuộc Configuration Layer khi cần, không hardcode URL trong từng Excel step nếu không cần.

## 6. Quy tắc Expected

`Expected` dùng cho verification.

Ví dụ:

```text
VerifyText
Target = HomePage.page_title
Expected = Welcome
```

## 7. Ma trận Keyword ↔ Target ↔ Data ↔ Expected

| Keyword | Target | Data | Expected |
|---|---|---|---|
| `Navigate` | Page key | Không | Không |
| `SetText` | Có | Có | Không |
| `ClickElement` | Có | Không | Không |
| `VerifyUrl` | Không | Không | Có |
| `VerifyText` | Có | Không | Có |
| `VerifyFieldState` | Có | Không | Có |
| `VerifyAttribute` | Có | Không | Có |
| `VerifyElement` | Có | Không | Có |
| `VerifyTextContains` | Có | Không | Có |
| `ClearText` | Có | Không | Không |
| `VerifyElementCount` | Có | Không | Có |
| `VerifyElementNotExist` | Có | Không | Không |
| `VerifyCalculation` | Có | Không | Có |
| `VerifyKeyword` | Có | Theo contract | Có |
| `AddToCart` | Có | Theo contract | Theo contract |
| `Login` | Theo contract | Theo contract | Theo contract |
| `VerifyDataMatch` | Có | Không | Có |
| `SetProductOutOfStock` | Có | Theo contract | Không |
| `ClickOutside` | Có | Không | Không |
| `SelectOption` | Có | Có | Không |

## 8. Mapping Keyword → POM

```text
SetText
Target = LoginPage.username_field
Data = admin
        ↓
KeywordRegistry.resolve("SetText")
        ↓
Keyword handler
        ↓
LoginPage.username_field
        ↓
LOCATORS
        ↓
BasePage.enter_text()
        ↓
Selenium
```

## 9. Naming Convention

### Keyword

```text
Navigate
SetText
ClickElement
VerifyText
```

### Page Object

```text
LoginPage
SearchPage
ProductPage
CartPage
```

### Element

```text
username_field
login_button
error_message
product_name
```

## 10. Lỗi Interface

Framework phải báo rõ:

1. Keyword không tồn tại.
2. Target sai format.
3. Page Object không tồn tại.
4. Element key không tồn tại.
5. Keyword yêu cầu Data nhưng Data thiếu.
6. Verification thiếu Expected.
7. Handler thực thi thất bại.

Lỗi nên có `TestCaseID`, `Step`, `Keyword`, `Target`.

## 11. Ví dụ hoàn chỉnh

### Login thành công

| TestCaseID | Step | Keyword | Target | Data | Expected |
|---|---:|---|---|---|---|
| TC_LOGIN_01 | 1 | Navigate | LoginPage | | |
| TC_LOGIN_01 | 2 | SetText | LoginPage.username_field | admin | |
| TC_LOGIN_01 | 3 | SetText | LoginPage.password_field | 123456 | |
| TC_LOGIN_01 | 4 | ClickElement | LoginPage.login_button | | |
| TC_LOGIN_01 | 5 | VerifyText | HomePage.page_title | | Welcome |

### Login thất bại

| TestCaseID | Step | Keyword | Target | Data | Expected |
|---|---:|---|---|---|---|
| TC_LOGIN_02 | 1 | Navigate | LoginPage | | |
| TC_LOGIN_02 | 2 | SetText | LoginPage.username_field | admin | |
| TC_LOGIN_02 | 3 | SetText | LoginPage.password_field | wrongpass | |
| TC_LOGIN_02 | 4 | ClickElement | LoginPage.login_button | | |
| TC_LOGIN_02 | 5 | VerifyText | LoginPage.error_message | | Invalid username or password |

## 12. Nguyên tắc cốt lõi

- Excel chỉ chứa test data và logical target.
- Keyword PascalCase.
- Browser lifecycle không xuất hiện trong Excel.
- `KeywordRegistry.resolve()` là interface chính thức.
- Target không chứa locator.
- Locator nằm trong Page Object.
- Không có `locators.py`.
- Test flow nằm ở Core Executor.
- Không có Test Layer → POM trực tiếp.
