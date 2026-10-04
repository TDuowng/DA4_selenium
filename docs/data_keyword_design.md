# Keyword Layer — Design Doc

## 1. Mục tiêu & phạm vi

Keyword Layer định nghĩa contract và cơ chế thực thi keyword.

Phạm vi:

- Chuẩn hóa tên keyword.
- Map keyword tới implementation.
- Resolve keyword qua `KeywordRegistry.resolve()`.
- Nhận `Target`, `Data`, `Expected` từ Test Executor.
- Không chứa locator Selenium trong Excel hoặc keyword.

Framework dùng một danh sách keyword chính thức; không tạo thêm nhánh business-keyword riêng.

## 2. Vị trí trong kiến trúc

```text
Excel
  ↓
TestExecutor
  ↓
KeywordExecutor
  ↓
KeywordRegistry.resolve()
  ↓
Keyword Implementation
  ↓
Page Object / BasePage
  ↓
Selenium
```

## 3. Keyword chính thức

Quy ước tên: **PascalCase**.

| Keyword | Nhóm | Target | Data | Expected | Mô tả |
|---|---|---|---|---|---|
| `Navigate` | Navigation | Page key | Không | Không | Điều hướng |
| `SetText` | Input | Có | Có | Không | Nhập text |
| `ClickElement` | Action | Có | Không | Không | Click element |
| `VerifyUrl` | Verification | Không | Không | Có | Kiểm tra URL |
| `VerifyText` | Verification | Có | Không | Có | Kiểm tra text |
| `VerifyFieldState` | Verification | Có | Không | Có | Kiểm tra trạng thái field |
| `VerifyAttribute` | Verification | Có | Không | Có | Kiểm tra attribute |
| `VerifyElement` | Verification | Có | Không | Có | Kiểm tra element |
| `VerifyTextContains` | Verification | Có | Không | Có | Kiểm tra text chứa chuỗi |
| `ClearText` | Input | Có | Không | Không | Xóa text |
| `VerifyElementCount` | Verification | Có | Không | Có | Kiểm tra số lượng |
| `VerifyElementNotExist` | Verification | Có | Không | Không | Kiểm tra element không tồn tại |
| `VerifyCalculation` | Verification | Có | Không | Có | Kiểm tra phép tính |
| `VerifyKeyword` | Verification | Có | Theo contract | Có | Placeholder cho verification keyword đã đăng ký |
| `AddToCart` | Action | Có | Theo contract | Theo contract | Thêm sản phẩm vào giỏ |
| `Login` | Action | Theo contract | Theo contract | Theo contract | Thực hiện thao tác login được expose |
| `VerifyDataMatch` | Verification | Có | Không | Có | So khớp dữ liệu |
| `SetProductOutOfStock` | Action | Có | Theo contract | Không | Thiết lập trạng thái hết hàng |
| `ClickOutside` | Action | Có | Không | Không | Click ngoài element |
| `SelectOption` | Action | Có | Có | Không | Chọn option |

`VerifyKeyword` là placeholder/interface pattern, không phải wildcard cho phép nhập keyword tùy ý vào Excel.

## 4. Browser lifecycle

Browser lifecycle là **System/Lifecycle**, không xuất hiện trong Excel.

```text
DriverManager + pytest fixture
```

Do đó không dùng:

```text
OpenBrowser
CloseBrowser
```

trong test step.

## 5. Test Data

Nguồn test case chính thức là Excel:

```text
data/test_cases.xlsx
```

Schema:

```text
TestCaseID | Step | Keyword | Target | Data | Expected
```

Không dùng JSON/CSV/SQLite làm nguồn test case chính.

## 6. Keyword Registry

### Interface chính thức

```python
class KeywordRegistry:
    def __init__(self, keyword_map):
        self._map = keyword_map

    def resolve(self, keyword):
        try:
            return self._map[keyword]
        except KeyError:
            raise KeyError(f"Keyword not registered: {keyword}")
```

`resolve()` là interface chính thức của Registry.

Có thể có map nội bộ:

```python
KEYWORD_MAP = {
    "Navigate": ...,
    "SetText": ...,
    "ClickElement": ...,
}
```

Nhưng `KeywordExecutor` không được gọi trực tiếp:

```python
KEYWORD_MAP["SetText"]
```

Mà phải gọi:

```python
registry.resolve("SetText")
```

## 7. Keyword Execution

`KeywordExecutor` nhận:

```text
keyword
Target
data
expected
context
```

và xử lý:

```text
resolve(keyword)
     ↓
handler
     ↓
target resolution
     ↓
POM/BasePage
```

## 8. Target

Target là logical reference:

```text
<PageObject>.<element>
```

Ví dụ:

```text
LoginPage.username_field
SearchPage.input
ProductPage.add_to_cart_button
```

Không ghi XPath/CSS/ID trong Excel.

## 9. Xử lý lỗi

Tối thiểu phải xử lý:

- Keyword không tồn tại.
- Target sai format.
- Page Object không tồn tại.
- Element key không tồn tại.
- Keyword yêu cầu Data nhưng Data thiếu.
- Verification thiếu Expected.
- Handler thực thi thất bại.

Lỗi nên có `TestCaseID`, `Step`, `Keyword`, `Target`.

## 10. Checklist

- [ ] Keyword PascalCase.
- [ ] Không có browser lifecycle trong Excel.
- [ ] Excel là nguồn test data chính.
- [ ] `KeywordRegistry.resolve()` là interface chính thức.
- [ ] KeywordExecutor không truy cập map nội bộ trực tiếp.
- [ ] Target là logical reference.
- [ ] Locator nằm trong Page Object.
