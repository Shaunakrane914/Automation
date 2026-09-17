import time
import undetected_chromedriver as uc

PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"

opts = uc.ChromeOptions()
opts.add_argument(f"--user-data-dir={PROFILE_DIR}")
opts.add_argument("--start-maximized")

print("Launching Undetected Chrome for Indeed...")
driver = uc.Chrome(options=opts, version_main=153)

try:
    print("Navigating to Indeed with Undetected Chrome...")
    driver.get("https://in.indeed.com/jobs?q=Machine+Learning+Intern&l=Remote")
    time.sleep(6)
    print("Indeed URL:", driver.current_url)
    print("Indeed Title:", driver.title)
    driver.save_screenshot(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\indeed_uc_test.png")
    
    cards = driver.find_elements("css selector", ".job_seen_beacon, div.cardOutline, td.resultContent")
    print(f"Found {len(cards)} job cards on Indeed with Undetected Chrome!")
finally:
    driver.quit()
