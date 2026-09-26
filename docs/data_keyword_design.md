# Keyword Layer — Design Doc

## 1. Mục tiêu & phạm vi

- Doc này mô tả thiết kế Keyword Engine — lớp điều phối đứng giữa
  Test Layer/Test Data và Page Object Layer.
- Không thay thế BasePage/Page Object; Keyword Engine chỉ tra registry
  và gọi lại các hàm đã có sẵn ở đó.
- Phạm vi: chỉ định nghĩa ~8-10 keyword cấp thấp cần cho các test case
  chính, không xây dựng engine tổng quát cho mọi trường hợp.

## 2. Vị trí trong kiến trúc tổng thể

- Test Layer gọi Keyword Engine cho từng bước test.
- Test Data cung cấp danh sách bước dạng (Keyword, Object, Value).
- Keyword Engine tra registry rồi gọi hàm thật trong Page Object/BasePage.

## 3. Danh sách Keyword

| Keyword              | Cấp  | Tham số             | Map tới hàm                    | Mô tả                                              |
| -------------------- | ---- | ------------------- | ------------------------------ | -------------------------------------------------- |
| OpenBrowser          | Thấp | url                 | `base_page.open_browser`       | Mở browser, load URL                               |
| CloseBrowser         | Thấp | —                   | `base_page.close_browser`      | Đóng browser                                       |
| InputText            | Thấp | object, value       | `base_page.type_text`          | Nhập text vào field                                |
| ClickElement         | Thấp | object              | `base_page.click`              | Click 1 element                                    |
| SelectDropdown       | Thấp | object, value       | `base_page.select_option`      | Chọn option trong dropdown                         |
| CheckCheckbox        | Thấp | object              | `base_page.check`              | Tick checkbox/radio                                |
| WaitForElement       | Thấp | object              | `base_page.wait_for_visible`   | Chờ element xuất hiện                              |
| VerifyText           | Thấp | object, value       | `base_page.assert_text_equals` | Assert nội dung text                               |
| VerifyElementVisible | Thấp | object              | `base_page.assert_visible`     | Assert element hiển thị                            |
| Login                | Cao  | username, password  | `login_page.login`             | Gộp: InputText×2 + ClickElement                    |
| Search               | Cao  | keyword             | `search_page.search`           | Gộp: InputText + ClickElement                      |
| SubmitForm           | Cao  | field_values (dict) | `form_page.submit_form`        | Gộp: nhiều InputText/SelectDropdown + ClickElement |

> Ghi chú: Keyword "Cao" là các hàm business-level đã có trong Page Object
> (ví dụ login, search) — được đăng ký thẳng vào registry, không viết lại logic mới.

## 4. Test Data cho Keyword (định dạng file test case)

### 4.2 Schema mỗi bước

- Step (số thứ tự)
- Keyword (tên keyword, phải tồn tại trong registry)
- Object (locator key, tra trong file locators)
- Value (dữ liệu nhập/kỳ vọng, có thể để trống)

## 5. Keyword Registry & Keyword Engine

### 5.1 Cấu trúc Registry

- Dict ánh xạ tên keyword → hàm thật (có ví dụ code)
- Quy ước đặt tên keyword (PascalCase, động từ + đối tượng)
- Ví dụ:

```python
        from pages.base_page import base_page
        from pages.login_page import login_page
        from pages.search_page import search_page
        from pages.form_page import form_page

        KEYWORD_REGISTRY = { # --- Keyword cấp thấp: map trực tiếp tới BasePage ---
        "OpenBrowser": base_page.open_browser,
        "CloseBrowser": base_page.close_browser,
        "InputText": base_page.type_text,
        "ClickElement": base_page.click,
        "SelectDropdown": base_page.select_option,
        "CheckCheckbox": base_page.check,
        "WaitForElement": base_page.wait_for_visible,
        "VerifyText": base_page.assert_text_equals,
        "VerifyElementVisible": base_page.assert_visible,

            # --- Keyword cấp cao: map tới Page Object business method ---
            "Login": login_page.login,
            "Search": search_page.search,
            "SubmitForm": form_page.submit_form,

        }
```

### 5.2 Keyword Engine — execute_keyword()

- Input: tên keyword, tham số
- Xử lý: tra registry → validate tham số → gọi hàm → bắt lỗi
- Output: kết quả / raise lỗi rõ tên keyword + bước đang chạy
- Ví dụ:

```python

    from keywords.registry import KEYWORD_REGISTRY
    from utils.logger import logger
    from utils.screenshot import take_screenshot

    def execute_keyword(step_number: int, keyword: str, \*args, \*\*kwargs):
    """
    Thực thi 1 keyword theo tên, log lại kết quả từng bước.
    step_number: số thứ tự bước, dùng để log/debug khi fail.
    keyword: tên keyword, phải có trong KEYWORD_REGISTRY.
    args/kwargs: tham số truyền vào hàm thật (object, value...).
    """
    if keyword not in KEYWORD_REGISTRY:
    raise ValueError(
    f"[Step {step_number}] Keyword '{keyword}' chưa được đăng ký trong registry"
    )

        action = KEYWORD_REGISTRY[keyword]
        logger.info(f"[Step {step_number}] Thực thi keyword '{keyword}' với args={args}")

        try:
            result = action(*args, **kwargs)
            logger.info(f"[Step {step_number}] Keyword '{keyword}' thành công")
            return result
        except Exception as e:
            logger.error(f"[Step {step_number}] Keyword '{keyword}' thất bại: {e}")
            take_screenshot(f"fail_step{step_number}_{keyword}")
            raise
```

### 5.3 Xử lý lỗi & logging

- Khi 1 keyword fail: log tên keyword, object, value, số bước
- Gọi Screenshot Utility trước khi raise lỗi (giữ nhất quán với Utility Layer)
- Ví dụ:

```python

  from keywords.registry import KEYWORD_REGISTRY
  from utils.logger import logger
  from utils.screenshot import take_screenshot

        def execute_keyword(step_number: int, keyword: str, *args, **kwargs):
            """
            Thực thi 1 keyword theo tên, log lại kết quả từng bước.
            step_number: số thứ tự bước, dùng để log/debug khi fail.
            keyword: tên keyword, phải có trong KEYWORD_REGISTRY.
            args/kwargs: tham số truyền vào hàm thật (object, value...).
            """
            if keyword not in KEYWORD_REGISTRY:
                raise ValueError(
                    f"[Step {step_number}] Keyword '{keyword}' chưa được đăng ký trong registry"
                )

            action = KEYWORD_REGISTRY[keyword]
            logger.info(f"[Step {step_number}] Thực thi keyword '{keyword}' với args={args}")

            try:
                result = action(*args, **kwargs)
                logger.info(f"[Step {step_number}] Keyword '{keyword}' thành công")
                return result
            except Exception as e:
                logger.error(f"[Step {step_number}] Keyword '{keyword}' thất bại: {e}")
                take_screenshot(f"fail_step{step_number}_{keyword}")
                raise
```

## 6. Luồng thực thi 1 test case bằng keyword

Test Layer đọc file test case → lặp qua từng bước →
gọi execute_keyword(step) → Keyword Engine gọi Page Object/BasePage →
kết quả từng bước được log lại → Reporting Layer tổng hợp

## 7. Giới hạn & việc không làm (Out of scope)

- Không hỗ trợ keyword lồng nhau (keyword gọi keyword) trong bản này
- Không tự sinh keyword mới từ UI, danh sách keyword là cố định, khai báo tay
- Không validate schema Test Data bằng thư viện riêng (làm thủ công trong loader)

## 8. Quy ước & checklist review

- [ ] Mọi keyword trong Test Data đều có trong registry
- [ ] Không có logic UI mới viết trực tiếp trong Keyword Engine
- [ ] Mỗi keyword có ít nhất 1 ví dụ trong mục 3
- [ ] Lỗi khi thực thi keyword đều được log kèm số bước
