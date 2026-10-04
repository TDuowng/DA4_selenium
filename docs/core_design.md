# Core Module Design

## 1. Mục đích

Core Layer điều phối việc chạy test. Core không chứa locator website và không chứa test flow riêng của từng chức năng.

```text
Excel Test Case
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
LOCATORS
      ↓
Selenium WebDriver
```

Browser lifecycle nằm ngoài Excel và do `DriverManager`/pytest fixture quản lý.

## 2. Các Core Modules

| Module | Trách nhiệm |
|---|---|
| `DriverManager` | Khởi tạo, cấu hình và cleanup WebDriver |
| `TestExecutor` | Đọc một TestCase và điều phối step theo thứ tự |
| `KeywordExecutor` | Thực thi từng step thông qua Registry |
| `TestContext` | Lưu driver và runtime context của test case |

Không có nhánh `Test Layer → Page Object` trực tiếp.

## 3. Driver Manager

### File

```text
core/driver_manager.py
```

### Chức năng

- Tạo Chrome WebDriver.
- Áp dụng browser configuration.
- Cấu hình timeout chung.
- Cung cấp driver cho pytest fixture/Core.
- Cleanup sau test.

`OpenBrowser` và `CloseBrowser` không xuất hiện trong Excel test step.

## 4. Test Executor

### File

```text
core/test_executor.py
```

### Input

Các step được đọc từ Excel:

```text
TestCaseID | Step | Keyword | Target | Data | Expected
```

### Xử lý

1. Lấy các step cùng `TestCaseID`.
2. Sắp xếp theo `Step`.
3. Tạo/nhận `TestContext`.
4. Gọi `KeywordExecutor` cho từng step.
5. Ghi nhận kết quả và lỗi.

## 5. Keyword Executor

### File

```text
core/keyword_executor.py
```

### Interface

```python
execute(keyword, target, data, expected, context)
```

Executor không truy cập trực tiếp dictionary keyword. Nó gọi:

```python
handler = registry.resolve(keyword)
```

sau đó thực thi handler theo contract của keyword.

## 6. Test Context

### File

```text
core/test_context.py
```

Có thể chứa:

- `driver`
- page-object cache
- execution metadata
- runtime variables nếu framework cần

## 7. Luồng xử lý chính

```text
pytest fixture
     ↓
DriverManager
     ↓
TestContext
     ↓
TestExecutor
     ↓
KeywordExecutor
     ↓
KeywordRegistry.resolve()
     ↓
Keyword handler
     ↓
Page Object / BasePage
     ↓
Selenium
```

## 8. Giới hạn

Core không:

- Chứa XPath/CSS/ID.
- Đọc locator trực tiếp từ Excel.
- Gọi Page Object trực tiếp từ Test Layer.
- Quản lý browser lifecycle bằng Excel keyword.
- Chứa business flow riêng của từng test case.

## 9. Nguyên tắc thiết kế

1. Một test case được điều phối bởi `TestExecutor`.
2. Một step được thực thi qua `KeywordExecutor`.
3. Keyword được resolve bằng `KeywordRegistry.resolve()`.
4. Browser do `DriverManager`/pytest fixture quản lý.
5. Locator thuộc Page Object.
6. Excel chỉ chứa test data và logical target.

## 10. Core Module Dependency

```text
tests
  ↓
TestExecutor
  ↓
KeywordExecutor
  ↓
KeywordRegistry
  ↓
Keyword Library
  ↓
POM
  ↓
Selenium

pytest fixture → DriverManager → TestContext
```

File chính thức:

```text
core/test_executor.py
```

Không sử dụng `test_excutor.py`.
