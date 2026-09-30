from pathlib import Path

from selenium.webdriver.common.by import By

from utils.excel_reader import ExcelReader


class LocatorReader:
    """Read UI locators from Excel."""

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

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.reader = ExcelReader(file_path)
        self._locators: dict[tuple[str, str], tuple[str, str]] = {}

    def load_sheet(self, sheet_name: str) -> None:
        rows = self.reader.read_sheet(sheet_name)

        for row in rows:
            page = self._normalize_name(row.get("Page"))
            element = self._normalize_name(row.get("Element"))
            locator_type = self._normalize_type(row.get("Type"))
            value = row.get("Value")

            if not page:
                raise ValueError("Cột Page không được trống.")

            if not element:
                raise ValueError("Cột Element không được trống.")

            if locator_type not in self.LOCATOR_TYPES:
                raise ValueError(
                    f"Locator chưa được khai báo "
                    f"'{locator_type}' cho "
                    f"{page}.{element}."
                )

            if value is None or str(value).strip() == "":
                raise ValueError(
                    f"Cột Value không được trống vị trí " f"{page}.{element}."
                )

            key = (page, element)

            if key in self._locators:
                raise ValueError(f"Locator trùng lặp: {page}.{element}")

            self._locators[key] = (self.LOCATOR_TYPES[locator_type], str(value).strip())

    def get_locator(self, page: str, element: str) -> tuple[str, str]:
        key = (self._normalize_name(page), self._normalize_name(element))

        if key not in self._locators:
            raise KeyError(f"Không tìm thấy Locator: {page}.{element}")

        return self._locators[key]

    # -- Hàm chuẩn hóa str cho Page và Element: "LoginPage ", "loginpage", "LoginPage"
    @staticmethod
    def _normalize_name(value) -> str:
        if value is None:
            return ""

        return str(value).strip().lower()

    @staticmethod
    def _normalize_type(value) -> str:
        if value is None:
            return ""

        return str(value).strip().upper()


_READER: "LocatorReader | None" = None


def get_locator_reader(file_path: str, sheet_name: str = "Locators") -> LocatorReader:
    """Tạo 1 lần, dùng lại cho mọi page."""
    global _READER
    if _READER is None:
        _READER = LocatorReader(file_path)
        _READER.load_sheet(sheet_name)
    return _READER
