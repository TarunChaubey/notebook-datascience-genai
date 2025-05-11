import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, WebDriverException, ElementNotInteractableException,
)

# LinkedIn credentials
username = ""  # Replace with your LinkedIn email
password = ""  # Replace with your LinkedIn password (use env variable or config file for production)

# URL of LinkedIn login page
url = "https://www.linkedin.com/login"
USER_DATA_DIR = "C:/Linkedin2"

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
chrome_options.add_argument("--profile-directory=Profile 1")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

# Initialize the Chrome driver
driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager().install()), options=chrome_options)

# Inject JavaScript to avoid detection
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        window.navigator.chrome = { runtime: {} };
    """
})

try:
    # Open LinkedIn login page
    driver.get(url)
    time.sleep(random.uniform(4, 6))  # Simulate natural wait

    # Locate input fields
    username_field = driver.find_element(By.ID, "username")
    password_field = driver.find_element(By.ID, "password")

    # Mimic typing
    for char in username:
        username_field.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

    for char in password:
        password_field.send_keys(char)
        time.sleep(random.uniform(0.05, 0.2))

    # Click the sign-in button
    sign_in_button = driver.find_element(By.CLASS_NAME, "btn__primary--large")
    sign_in_button.click()

    # Wait to verify successful login (adjust for your network speed)
    time.sleep(random.uniform(110, 200))

    # You can now navigate further
    print("✅ Login successful!")

except (NoSuchElementException, WebDriverException, TimeoutException, ElementNotInteractableException) as e:
    print(f"❌ Error occurred: {e}")

finally:
    print("⏹️ Closing the browser...")
    driver.quit()
