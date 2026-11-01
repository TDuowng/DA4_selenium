from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / "data"
EXCEL_DIR = DATA_DIR / "excel"
EXCEL_FILE = EXCEL_DIR / "login_hybrid.xlsx"
LOCATOR_FILE = EXCEL_DIR / "locators.xlsx"
ARTIFACTS_DIR = ROOT / "artifacts"

SITE_CONFIG = {
    "demoQA": {"url": "https://demoqa.com/login", "locator_sheet": "demoQA"},
    "ts": {
        "url": "https://itsaki5.github.io/the_souvenirs/login.html",
        "locator_sheet": "ts",
    },
    "taophoBA": {
        "url": "https://tduowng.github.io/Web-TPBA-main/login.html",
        "locator_sheet": "taophoBA",
    },
}

TIMEOUT = 15

BROWSER = "chrome"

# Tài khoản mặc định cho keyword Login (mật khẩu lấy từ biến môi trường, không ghi vào code)
DEFAULT_USERNAME = "validUser"
DEFAULT_PASSWORD = os.getenv("TEST_PASSWORD", "")
