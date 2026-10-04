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
    driver.get("https://demoqa.com/login")

    # Step 2: fill "input"
    field_2 = wait.until(EC.visibility_of_element_located((By.ID, "userName")))
    field_2.clear()
    field_2.send_keys("validUser")

    # Step 3: fill "input"
    field_3 = wait.until(EC.visibility_of_element_located((By.ID, "password")))
    field_3.clear()
    field_3.send_keys(os.getenv("TEST_PASSWORD", ""))

    # Step 4: click "Login"
    element_4 = wait.until(EC.element_to_be_clickable((By.ID, "login")))
    element_4.click()

    # Step 5: click "validUser"
    element_5 = wait.until(EC.element_to_be_clickable((By.ID, "userName-value")))
    element_5.click()

    # Step 6: click "User Name :"
    element_6 = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                "//*[@id='books-wrapper']//label[normalize-space()='User Name :']",
            )
        )
    )
    element_6.click()

    # Step 7: click "validUser"
    element_7 = wait.until(EC.element_to_be_clickable((By.ID, "userName-value")))
    element_7.click()
finally:
    driver.quit()
