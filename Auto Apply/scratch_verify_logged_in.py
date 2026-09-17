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
    print("Navigating to Internshala tech internships (WFH)...")
    driver.get("https://internshala.com/internships/matching-preferences/")
    time.sleep(4)
    print("Internshala URL:", driver.current_url)
    print("Internshala Title:", driver.title)
    driver.save_screenshot(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\logged_in_internshala_matching.png")

    driver.get("https://internshala.com/internships/work-from-home-python%2Fdjango,machine-learning,artificial-intelligence-ai-internships/")
    time.sleep(4)
    print("Internshala Search URL:", driver.current_url)
    driver.save_screenshot(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\logged_in_internshala_search.png")

    cards = driver.find_elements(By.CSS_SELECTOR, ".individual_internship")
    print(f"Found {len(cards)} internships on Internshala!")

    print("\nNavigating to LinkedIn Jobs (Remote)...")
    driver.get("https://www.linkedin.com/jobs/search/?keywords=AI%20Engineer%20Intern&f_WT=2&f_AL=true")
    time.sleep(5)
    print("LinkedIn Jobs URL:", driver.current_url)
    print("LinkedIn Title:", driver.title)
    driver.save_screenshot(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\logged_in_linkedin_jobs.png")

    ln_cards = driver.find_elements(By.CSS_SELECTOR, ".job-card-container, .jobs-search-results-list li")
    print(f"Found {len(ln_cards)} LinkedIn Easy Apply job cards!")

finally:
    driver.quit()
