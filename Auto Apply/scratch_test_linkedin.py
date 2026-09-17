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
    print("Navigating to LinkedIn login...")
    driver.get("https://www.linkedin.com/login")
    time.sleep(4)
    
    # Find all displayed email inputs
    email_inputs = [i for i in driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']") if i.is_displayed()]
    password_inputs = [i for i in driver.find_elements(By.CSS_SELECTOR, "input[type='password']") if i.is_displayed()]
    
    print(f"Found {len(email_inputs)} visible email inputs, {len(password_inputs)} visible password inputs")
    
    if email_inputs and password_inputs:
        u = email_inputs[0]
        u.clear()
        u.send_keys("shaunakrane914@gmail.com")
        print("Entered email into visible field")
        time.sleep(1)
        
        p = password_inputs[0]
        p.clear()
        p.send_keys("Shaunak34@ra")
        print("Entered password into visible field")
        time.sleep(1)
        
        submit_buttons = [b for b in driver.find_elements(By.CSS_SELECTOR, "button[type='submit']") if b.is_displayed()]
        if submit_buttons:
            print("Clicking submit button...")
            submit_buttons[0].click()
        else:
            p.send_keys("\n")
            
        time.sleep(8)
        
    print("Final URL:", driver.current_url)
    print("Final Title:", driver.title)
    driver.save_screenshot(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\linkedin_after_login.png")

finally:
    driver.quit()
