from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / "data"
EXCEL_DIR = DATA_DIR / "excel"
EXCEL_FILE = EXCEL_DIR / "login_hybrid.xlsx"
LOCATOR_FILE = EXCEL_DIR / "locators.xlsx"
ARTIFACTS_DIR = ROOT / "artifacts"

TIMEOUT = 15
PAGE_LOAD_TIMEOUT = 45

BROWSER = "chrome"

# Tài khoản mặc định cho keyword Login (mật khẩu lấy từ biến môi trường, không ghi vào code)
DEFAULT_USERNAME = "validUser"
DEFAULT_PASSWORD = os.getenv("TEST_PASSWORD", "")
