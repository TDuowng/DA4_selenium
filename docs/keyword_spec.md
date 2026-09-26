# Keyword Specification

## 1. Mục đích

Tài liệu này đặc tả **Keyword Library** của framework kiểm thử tự động.

Framework sử dụng mô hình Keyword-Driven kết hợp Page Object Model (POM). Mỗi keyword mô tả một hành động hoặc một bước xác minh của test case và được ánh xạ tới một hàm thực thi cụ thể.

Nguyên tắc:

- Keyword được viết bằng tên chuẩn, thống nhất giữa Excel và source code.
- Keyword không chứa locator cụ thể của website.
- Keyword không đọc trực tiếp XPath/CSS/ID từ Excel.
- Keyword sử dụng `Target` để xác định phần tử thông qua Page Object.
- `Data` dùng cho dữ liệu đầu vào của thao tác.
- `Expected` chỉ dùng cho các bước verification.
- Browser lifecycle (`OPEN_BROWSER`, `CLOSE_BROWSER`) do framework/fixture quản lý, không phải test step thông thường trong Excel.

## 2. Phạm vi Keyword

Keyword được chia thành các nhóm:

| Nhóm             | Mục đích                                                           |
| ---------------- | ------------------------------------------------------------------ |
| Navigation       | Điều hướng trình duyệt/trang                                       |
| Input            | Nhập hoặc xóa dữ liệu trên element                                 |
| Action           | Thao tác với element                                               |
| Verification     | Kiểm tra kết quả mong đợi                                          |
| System/Lifecycle | Quản lý tài nguyên framework, không ghi như test step thông thường |

---

## 3. Quy ước tên Keyword

Tên keyword:

- Có ý nghĩa nghiệp vụ rõ ràng.
- Không chứa locator.
- Không phụ thuộc tên website cụ thể.

Ví dụ:

```text
NavigateURL
InputText
Click
VerifyURL
```

Không dùng:

```text
CLICK_USERNAME_XPATH
ENTER_TEXT_ID_USERNAME
VERIFY_LOGIN_XPATH
```

vì keyword không nên gắn với một locator cụ thể.

---

## 4. Keyword list chính thức

### 4.1 Navigation

| Keyword    | Target | Data  | Expected | Mô tả                  |
| ---------- | ------ | ----- | -------- | ---------------------- |
| `NAVIGATE` | Không  | URL   | Không    | Mở URL cần kiểm thử    |
| `BACK`     | Không  | Không | Không    | Quay lại trang trước   |
| `REFRESH`  | Không  | Không | Không    | Tải lại trang hiện tại |

Ví dụ:

```text
Keyword = NAVIGATE
Target =
Data = https://example.com/login
Expected =
```

---

### 4.2 Input

| Keyword      | Target | Data  | Expected | Mô tả                    |
| ------------ | ------ | ----- | -------- | ------------------------ |
| `ENTER_TEXT` | Có     | Text  | Không    | Nhập dữ liệu vào element |
| `CLEAR_TEXT` | Có     | Không | Không    | Xóa nội dung của element |

Ví dụ:

```text
Keyword = ENTER_TEXT
Target = LoginPage.username_field
Data = admin
Expected =
```

`ENTER_TEXT` là keyword có `Data`.

---

### 4.3 Action

| Keyword | Target | Data  | Expected | Mô tả         |
| ------- | ------ | ----- | -------- | ------------- |
| `CLICK` | Có     | Không | Không    | Click element |

Ví dụ:

```text
Keyword = CLICK
Target = LoginPage.login_button
Data =
Expected =
```

---

### 4.4 Verification

| Keyword                  | Target | Data  | Expected      | Mô tả                     |
| ------------------------ | ------ | ----- | ------------- | ------------------------- |
| `VERIFY_TEXT`            | Có     | Không | Text          | Kiểm tra text của element |
| `VERIFY_URL`             | Không  | Không | URL/Text      | Kiểm tra URL hiện tại     |
| `VERIFY_ELEMENT_VISIBLE` | Có     | Không | Không         | Kiểm tra element hiển thị |
| `VERIFY_ERROR`           | Có     | Không | Error message | Kiểm tra thông báo lỗi    |

Ví dụ:

```text
Keyword = VERIFY_TEXT
Target = HomePage.page_title
Data =
Expected = Welcome
```

Ví dụ kiểm tra lỗi:

```text
Keyword = VERIFY_ERROR
Target = LoginPage.error_message
Data =
Expected = Invalid username or password
```

`VERIFY_ERROR` dùng để chuẩn hóa việc xác minh lỗi. Cách website hiển thị lỗi có thể khác nhau; Page Object chịu trách nhiệm xác định element/locator tương ứng.

---

## 5. System/Lifecycle Keywords

Các keyword sau có thể tồn tại trong Keyword Library nhưng **không bắt buộc xuất hiện trong Excel test step**:

```text
OPEN_BROWSER
CLOSE_BROWSER
```

Lý do:

- Browser được khởi tạo bởi `DriverManager`/pytest fixture.
- Browser được cleanup sau test.
- Test case tập trung mô tả hành vi cần kiểm thử thay vì quản lý tài nguyên framework.

Do đó test case có thể bắt đầu từ:

```text
NAVIGATE
```

thay vì:

```text
OPEN_BROWSER
NAVIGATE
```

---

## 6. Keyword Interface

Mỗi keyword được thực thi thông qua một interface thống nhất:

```text
execute(keyword, target, data, expected, context)
```

Trong đó:

| Parameter  | Ý nghĩa                                   |
| ---------- | ----------------------------------------- |
| `keyword`  | Tên keyword                               |
| `target`   | Đối tượng UI cần thao tác, nếu có         |
| `data`     | Dữ liệu đầu vào, nếu có                   |
| `expected` | Giá trị mong đợi cho verification, nếu có |
| `context`  | Trạng thái hiện tại của test              |

Ví dụ:

```text
execute(
    keyword="ENTER_TEXT",
    target="LoginPage.username_field",
    data="admin",
    expected="",
    context=context
)
```

---

## 7. Keyword Registry

Keyword được ánh xạ tới hàm thực thi thông qua registry.

Ví dụ thiết kế:

```python
REGISTRY = {
    "NAVIGATE": navigate,
    "BACK": back,
    "REFRESH": refresh,
    "ENTER_TEXT": enter_text,
    "CLEAR_TEXT": clear_text,
    "CLICK": click,
    "VERIFY_TEXT": verify_text,
    "VERIFY_URL": verify_url,
    "VERIFY_ELEMENT_VISIBLE": verify_element_visible,
    "VERIFY_ERROR": verify_error,
}
```

Registry là nơi xác định:

```text
Keyword trong Excel
        ↓
Keyword Registry
        ↓
Hàm keyword tương ứng
```

---

## 8. Quy tắc Target

Keyword không chứa locator.

Ví dụ đúng:

```text
ENTER_TEXT
Target = LoginPage.username_field
Data = admin
```

Ví dụ không đúng:

```text
ENTER_TEXT
Target = //input[@id='username']
Data = admin
```

Target được phân giải qua Page Object theo quy định trong `interface_spec.md` và `pom_design.md`.

---

## 9. Quy tắc Data và Expected

### Data

`Data` là dữ liệu đầu vào cho thao tác.

Ví dụ:

```text
ENTER_TEXT → Data = admin
NAVIGATE → Data = https://example.com
```

Các keyword không cần dữ liệu để thực hiện thì để trống.

### Expected

`Expected` chỉ được sử dụng cho các keyword verification.

Ví dụ:

```text
VERIFY_TEXT → Expected = Login successful
VERIFY_URL → Expected = /dashboard
VERIFY_ERROR → Expected = Invalid username or password
```

Các keyword thao tác thông thường không ghi Expected.

---

## 10. Keyword Result

Keyword execution nên trả về kết quả chuẩn hóa, ví dụ:

```text
status
actual
error
```

Thiết kế khái niệm:

```text
KeywordResult
├── status
├── actual
├── message
└── error
```

Ví dụ verification thành công:

```text
status = PASS
actual = "Login successful"
message = ""
error = ""
```

Ví dụ verification thất bại:

```text
status = FAIL
actual = "Invalid password"
message = "Expected: Login successful"
error = ""
```

---

## 11. Nguyên tắc thiết kế

1. Keyword chỉ mô tả hành động hoặc verification.
2. Locator thuộc Page Object, không thuộc Keyword.
3. Keyword không phụ thuộc trực tiếp vào tên website.
4. Keyword có interface nhất quán.
5. Keyword có thể được tái sử dụng cho nhiều Page Object.
6. Verification phải có cơ chế xác định PASS/FAIL dựa trên Expected hoặc điều kiện kiểm tra.
7. Browser lifecycle được quản lý bởi framework thay vì lặp lại trong từng test case.
