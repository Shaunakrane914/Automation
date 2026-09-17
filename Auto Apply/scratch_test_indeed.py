import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"

opts = Options()
opts.binary_location = CHROME_EXE
opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
opts.add_argument("--start-maximized")
opts.add_argument("--disable-blink-features=AutomationControlled")
opts.add_experimental_option("excludeSwitches", ["enable-automation"])
opts.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(options=opts)

try:
    print("Testing Indeed remote internship search with persistent profile...")
    driver.get("https://in.indeed.com/jobs?q=Machine+Learning+Intern&l=Remote")
    time.sleep(5)
    
    # Dismiss cookie banner if present
    try:
        accept_btn = driver.find_element(By.ID, "onetrust-accept-btn-handler")
        if accept_btn.is_displayed():
            accept_btn.click()
            time.sleep(1)
    except Exception:
        pass

    print("Indeed URL:", driver.current_url)
    print("Indeed Title:", driver.title)
    driver.save_screenshot(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\indeed_search_test.png")
    
    # Check for job cards
    cards = driver.find_elements(By.CSS_SELECTOR, ".job_seen_beacon, div.cardOutline")
    print(f"Found {len(cards)} job cards on Indeed!")

finally:
    driver.quit()
