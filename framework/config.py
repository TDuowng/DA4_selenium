from pathlib import Path

ROOT = Path(__file__).resolve().parent

DATA_DIR = ROOT / "data"
EXCEL_DIR = DATA_DIR / "excel"
EXCEL_FILE = EXCEL_DIR / "test_data.xlsx"  # gồm 2 sheet: test_steps, test_case

LOGIN_URL = {"login": "https://demoqa.com/login"}

TIMEOUT = 15
