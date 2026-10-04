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
    element_4 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Login']")))
    element_4.click()

    # Step 5: click "You logged into a secure area!"
    element_5 = wait.until(EC.element_to_be_clickable((By.ID, "flash")))
    element_5.click()

    # Step 6: click "Welcome to the Secure Area. When you are done click logout below."
    element_6 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "h4.subheader")))
    element_6.click()

    # Step 7: click "Secure Area"
    element_7 = wait.until(EC.element_to_be_clickable((By.XPATH, "//h2[normalize-space()='Secure Area']")))
    element_7.click()

    # Step 8: click "Logout"
    element_8 = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[normalize-space()='Logout']")))
    element_8.click()
finally:
    driver.quit()
