import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

print("Launching visible Chrome with persistent profile...")
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 15)

try:
    print("\n--- TESTING INTERNSHALA LOGIN ---")
    driver.get("https://internshala.com")
    time.sleep(4)
    
    # 1. Check if promo popup exists and dismiss it
    try:
        close_btn = driver.find_element(By.CSS_SELECTOR, "#close_popup, .modal-close, button[aria-label='Close'], .close_button")
        if close_btn.is_displayed():
            print("Dismissing promo popup...")
            close_btn.click()
            time.sleep(1)
    except Exception:
        pass

    # Check if already logged in
    is_logged_in = False
    try:
        prof_icon = driver.find_element(By.CSS_SELECTOR, ".profile_icon, #profile_dropdown, .user_profile_holder")
        if prof_icon.is_displayed():
            is_logged_in = True
            print("Already logged in to Internshala!")
    except Exception:
        pass

    if not is_logged_in:
        print("Clicking login button...")
        try:
            login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".login-cta, a[href*='login']")))
            login_btn.click()
            time.sleep(2)
        except Exception as e:
            print("Login button click error, navigating directly to login:", e)
            driver.get("https://internshala.com/login/user")
            time.sleep(3)

        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#modal_email, #email, input[type='email']")))
        email_input.clear()
        email_input.send_keys("shaunakrane914@gmail.com")
        time.sleep(1)

        pass_input = driver.find_element(By.CSS_SELECTOR, "#modal_password, #password, input[type='password']")
        pass_input.clear()
        pass_input.send_keys("shaunak43rane")
        time.sleep(1)

        submit_btn = driver.find_element(By.CSS_SELECTOR, "#modal_login_submit, button[type='submit']")
        print("Submitting login credentials...")
        submit_btn.click()
        time.sleep(6)

    print("Internshala current URL:", driver.current_url)
    driver.save_screenshot(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\test_internshala_result.png")

    print("\n--- TESTING LINKEDIN LOGIN ---")
    driver.get("https://www.linkedin.com/login")
    time.sleep(3)

    if "feed" in driver.current_url:
        print("Already logged in to LinkedIn!")
    else:
        try:
            user_el = driver.find_element(By.ID, "username")
            user_el.clear()
            user_el.send_keys("shaunakrane914@gmail.com")
            time.sleep(1)

            pass_el = driver.find_element(By.ID, "password")
            pass_el.clear()
            pass_el.send_keys("Shaunak34@ra")
            time.sleep(1)

            submit = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            print("Submitting LinkedIn login...")
            submit.click()
            time.sleep(6)
        except Exception as ln_e:
            print("LinkedIn form error:", ln_e)

    print("LinkedIn current URL:", driver.current_url)
    driver.save_screenshot(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\test_linkedin_result.png")

    print("\n--- TESTING INDEED LOGIN ---")
    driver.get("https://in.indeed.com/account/login")
    time.sleep(4)
    print("Indeed current URL:", driver.current_url)
    driver.save_screenshot(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\test_indeed_result.png")

    # If email field exists on Indeed
    try:
        e_box = driver.find_element(By.CSS_SELECTOR, "input[type='email'], #ifl-InputFormField-3")
        if e_box.is_displayed():
            print("Entering Indeed email...")
            e_box.clear()
            e_box.send_keys("shaunakrane914@gmail.com")
            driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
            time.sleep(4)
            p_box = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
            if p_box.is_displayed():
                print("Entering Indeed password...")
                p_box.clear()
                p_box.send_keys("shaunak43rane")
                driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                time.sleep(5)
    except Exception as ind_e:
        print("Indeed login note:", ind_e)

    print("Indeed final URL:", driver.current_url)
    driver.save_screenshot(r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\test_indeed_final.png")

finally:
    time.sleep(2)
    driver.quit()
    print("Test run completed!")
