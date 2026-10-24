"""
QA Script Recorder | Selenium Python | Beginner
Selenium 4.27.0
"""

import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

try:
    # Step 1: navigate to the recorded page
    driver.get("https://the-internet.herokuapp.com/login")

    # Step 2: fill "input"
    field_2 = wait.until(EC.visibility_of_element_located((By.ID, "username")))
    field_2.clear()
    field_2.send_keys("tomsmith")

    # Step 3: fill "input"
    field_3 = wait.until(EC.visibility_of_element_located((By.ID, "password")))
    field_3.clear()
    field_3.send_keys(os.getenv("TEST_PASSWORD", ""))

    # Step 4: click "Login"
    element_4 = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Login']"))
    )
    element_4.click()

    # Step 5: click "You logged into a secure area!"
    element_5 = wait.until(EC.element_to_be_clickable((By.ID, "flash")))
    element_5.click()

    # Step 6: click "Welcome to the Secure Area. When you are done click logout below."
    element_6 = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "h4.subheader"))
    )
    element_6.click()

    # Step 7: click "Secure Area"
    element_7 = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//h2[normalize-space()='Secure Area']"))
    )
    element_7.click()

    # Step 8: click "Logout"
    element_8 = wait.until(
        EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Logout']"))
    )
    element_8.click()
finally:
    driver.quit()

FIELDS = {"case_id", "step", "keyword", "target", "data", "expected"}


def validate_steps(self, steps: list[dict[str, str]]) -> list[dict[str, str]]:
    if not isinstance(steps, list) or not steps:
        raise ValueError("Kịch bản không có bước")

    first_row = steps[0]
    case_id = first_row.get("case_id") if isinstance(first_row, dict) else None
    canonical_keywords = []

    for index, row in enumerate(steps, 1):
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError(f"Bước {index}: sai schema")
        if any(not isinstance(value, str) for value in row.values()):
            raise ValueError(f"Bước {index}: dữ liệu phải là chuỗi")
        if not case_id or row["case_id"] != case_id or row["step"] != str(index):
            raise ValueError(f"Bước {index}: sai case_id hoặc thứ tự step")

        try:
            canonical_keywords.append(
                self.keyword_executor.registry.canonical_name(row["keyword"])
            )
        except (KeyError, TypeError) as exc:
            raise ValueError(f"Bước {index}: {exc}") from exc

    if canonical_keywords[0] != "Navigate":
        raise ValueError("Bước đầu phải là Navigate")
    if not any(keyword.startswith("Verify") for keyword in canonical_keywords):
        raise ValueError("Kịch bản cần ít nhất một bước Verify")

    return steps
