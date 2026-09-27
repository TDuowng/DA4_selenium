# Keyword Specification

## 1. Mục đích

Đặc tả Keyword Library của framework kiểm thử tự động.

Framework kết hợp Keyword-Driven Testing, Data-Driven Testing và POM.

Nguyên tắc:

- Keyword dùng tên chuẩn thống nhất giữa Excel và source code.
- Keyword dùng PascalCase.
- Keyword không chứa locator cụ thể.
- Keyword dùng Target để xác định Page Object/element.
- Data dùng cho input.
- Expected dùng cho verification.
- Browser lifecycle do DriverManager/pytest fixture quản lý.

## 2. Phạm vi Keyword

| Nhóm | Mục đích |
|---|---|
| Navigation | Điều hướng |
| Input | Nhập/xóa dữ liệu |
| Action | Thao tác UI |
| Verification | Kiểm tra kết quả |
| System/Lifecycle | Quản lý browser/framework, không xuất hiện trong Excel |

## 3. Quy ước tên

PascalCase:

```text
Navigate
SetText
ClickElement
VerifyText
VerifyUrl
```

Không gắn locator vào tên keyword.

## 4. Keyword list chính thức

### Navigation

`Navigate`

### Input

`SetText`

`ClearText`

### Action

`ClickElement`

`AddToCart`

`Login`

`SetProductOutOfStock`

`ClickOutside`

`SelectOption`

### Verification

`VerifyUrl`

`VerifyText`

`VerifyFieldState`

`VerifyAttribute`

`VerifyElement`

`VerifyTextContains`

`VerifyElementCount`

`VerifyElementNotExist`

`VerifyCalculation`

`VerifyKeyword`

`VerifyDataMatch`

Danh sách trên là contract chính thức. Không tự ý thêm keyword vào Excel nếu chưa có implementation/registry entry.

## 5. System/Lifecycle

Browser lifecycle không phải test step trong Excel.

```text
DriverManager + pytest fixture
```

Không dùng `OpenBrowser`/`CloseBrowser` trong Excel.

Test case có thể bắt đầu bằng:

```text
Navigate
```

## 6. Keyword Interface

Execution interface:

```python
execute(keyword, target, data, expected, context)
```

Execution layer resolve handler bằng:

```python
registry.resolve(keyword)
```

`resolve()` là Registry interface, không phải keyword.

## 7. Keyword Registry

```python
class KeywordRegistry:
    def __init__(self, keyword_map):
        self._map = keyword_map

    def resolve(self, keyword):
        if keyword not in self._map:
            raise KeyError(f"Keyword not registered: {keyword}")
        return self._map[keyword]
```

Có thể có `KEYWORD_MAP` nội bộ, nhưng `KeywordExecutor` không truy cập trực tiếp map.

## 8. Target

Format:

```text
<PageObject>.<element>
```

Ví dụ:

```text
LoginPage.username_field
SearchPage.input
ProductPage.add_to_cart_button
```

## 9. Data và Expected

`SetText` và `SelectOption` có input Data theo contract hiện tại.

Verification dùng Expected theo contract của từng keyword.

Chi tiết schema nằm trong `interface_spec.md`.

## 10. Keyword Result

Handler phải trả về hoặc phát sinh kết quả đủ để Executor ghi nhận:

- pass/fail;
- message lỗi;
- runtime state nếu có.

Verification thất bại phải cung cấp thông tin TestCaseID/Step khi báo lỗi.

## 11. Nguyên tắc thiết kế

1. PascalCase là naming convention chính thức.
2. Keyword không chứa locator.
3. Browser lifecycle không nằm trong Excel.
4. Excel là nguồn test data chính.
5. `KeywordRegistry.resolve()` là Registry interface chính thức.
6. KeywordExecutor không truy cập map nội bộ trực tiếp.
7. Target là logical reference.
8. Locator nằm trong Page Object.
9. Test flow nằm trong Core Executor.
10. Không có Test Layer → POM trực tiếp.
