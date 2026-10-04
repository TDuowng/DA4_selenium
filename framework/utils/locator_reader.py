# Đọc locator từ locators.xlsx. Mỗi sheet = 1 website/nhóm trang, cột: Page | Element | Type | Value.
# Toàn bộ sheet được nạp 1 lần và kiểm tra ngay (trước khi mở browser).
# Tên Page/Element KHÔNG phân biệt hoa thường ("LoginPage.Username" khớp "username").
# Tên Page phải duy nhất trên TẤT CẢ sheet (trùng sẽ báo lỗi).

from pathlib import Path

from openpyxl import load_workbook
from selenium.webdriver.common.by import By

REQUIRED_COLUMNS = ("Page", "Element", "Type", "Value")


class LocatorReader:
    LOCATOR_TYPES = {
        "ID": By.ID,
        "NAME": By.NAME,
        "CLASS_NAME": By.CLASS_NAME,
        "TAG_NAME": By.TAG_NAME,
        "LINK_TEXT": By.LINK_TEXT,
        "PARTIAL_LINK_TEXT": By.PARTIAL_LINK_TEXT,
        "CSS_SELECTOR": By.CSS_SELECTOR,
        "XPATH": By.XPATH,
    }

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self._locators: dict[tuple[str, str], tuple[str, str]] = {}
        self._source: dict[tuple[str, str], str] = (
            {}
        )  # key -> tên sheet, để báo lỗi trùng

    def load_all(self) -> "LocatorReader":
        workbook = load_workbook(self.file_path, read_only=True, data_only=True)

        try:
            for sheet in workbook.worksheets:
                self._load_sheet(sheet.title, sheet.iter_rows(values_only=True))
        finally:
            workbook.close()

        if not self._locators:
            raise ValueError(f"{self.file_path.name}: không có locator nào")

        return self

    def _load_sheet(self, sheet_name, rows):
        rows = iter(rows)

        header = next(rows, None)

        if header is None:
            raise ValueError(f"Sheet '{sheet_name}': trống")

        columns = {str(h).strip(): i for i, h in enumerate(header) if h is not None}

        missing = [c for c in REQUIRED_COLUMNS if c not in columns]

        if missing:
            raise ValueError(f"Sheet '{sheet_name}': thiếu cột {missing}")

        for line, row in enumerate(rows, start=2):
            if all(c is None or str(c).strip() == "" for c in row):
                continue  # bỏ dòng trống hoàn toàn

            get = lambda name: (
                row[columns[name]] if columns[name] < len(row) else None
            )

            page = self._norm(get("Page"))
            element = self._norm(get("Element"))

            locator_type = str(get("Type") or "").strip().upper()

            value = "" if get("Value") is None else str(get("Value")).strip()

            where = f"Sheet '{sheet_name}' dòng {line}"

            if not page or not element:
                raise ValueError(f"{where}: Page/Element không được trống")

            if locator_type not in self.LOCATOR_TYPES:
                raise ValueError(
                    f"{where}: Type '{locator_type}' "
                    f"không hỗ trợ ({page}.{element})"
                )

            if not value:
                raise ValueError(f"{where}: Value trống ({page}.{element})")

            key = (page, element)

            if key in self._locators:
                raise ValueError(
                    f"{where}: trùng locator {page}.{element} "
                    f"(đã có ở sheet '{self._source[key]}')"
                )

            self._locators[key] = (self.LOCATOR_TYPES[locator_type], value)

            self._source[key] = sheet_name

    def has_locator(self, page, element) -> bool:
        return (self._norm(page), self._norm(element)) in self._locators

    def get_locator(self, page, element) -> tuple[str, str]:
        key = (self._norm(page), self._norm(element))

        if key not in self._locators:
            raise KeyError(f"Không tìm thấy Locator: {page}.{element}")

        return self._locators[key]

    # -- Hàm chuẩn hóa str cho Page và Element:
    # "LoginPage ", "loginpage", "LoginPage"
    @staticmethod
    def _norm(value) -> str:
        return "" if value is None else str(value).strip().lower()


_READERS: dict[str, LocatorReader] = {}


def get_locator_reader(file_path) -> LocatorReader:
    """Nạp 1 lần cho mỗi file, dùng lại cho mọi page."""
    key = str(Path(file_path).resolve())

    if key not in _READERS:
        _READERS[key] = LocatorReader(key).load_all()

    return _READERS[key]
