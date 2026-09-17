import subprocess
import time
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA = r"C:\Users\Shaunak Rane\AppData\Local\Google\Chrome\User Data"
URL = "https://in.indeed.com/account/login"

print("Starting Chrome with user profile and remote debugging on 9222...")
cmd = [CHROME_EXE, f"--user-data-dir={USER_DATA}", "--profile-directory=Default", "--remote-debugging-port=9222", "--start-maximized", URL]
proc = subprocess.Popen(cmd)
time.sleep(4)

print("Connecting via CDP...")
with sync_playwright() as p:
    try:
        browser = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
        print("Connected via CDP!")
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        time.sleep(3)
        print("Page URL:", page.url)

        # Look for Continue with Google or Shaunak account
        print("Looking for Google button or account on page...")
        g_btn = page.locator("div[role='button']:has-text('Continue with Google'), #button-label, span:has-text('Continue with Google')").first
        if g_btn.is_visible(timeout=5000):
            print("Found Continue with Google! Clicking it now...")
            g_btn.click()
            time.sleep(5)
            print("After click URL:", page.url)

        time.sleep(5)
        page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\indeed_user_chrome_proof.png")
        print("Captured screenshot to indeed_user_chrome_proof.png")
    except Exception as e:
        print("CDP note:", e)

print("Leaving Chrome open on screen for user!")
