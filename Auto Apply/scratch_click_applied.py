import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch_persistent_context(
        user_data_dir=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent",
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=False,
        args=["--start-maximized"]
    )
    page = b.pages[0]
    page.goto("https://www.linkedin.com/my-items/saved-jobs/", wait_until="domcontentloaded")
    time.sleep(3)
    
    info = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a, button'))
            .filter(e => e.innerText && e.innerText.includes('Applied'))
            .map(e => ({ tag: e.tagName, text: e.innerText, href: e.href || '' }));
    }""")
    print("Found Applied elements:", info)
    
    # Click the element
    btn = page.locator("a:has-text('Applied'), button:has-text('Applied')").first
    btn.click(force=True)
    time.sleep(4)
    
    page.screenshot(path=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\logs\screenshots\real_linkedin_applied_43_list.png")
    
    applied_titles = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('.job-card-list__title, .entity-result__title-text, .reusable-search__result-container'))
            .map(e => e.innerText.trim())
            .filter(t => t.length > 0);
    }""")
    print("Applied titles:", applied_titles[:10])

    b.close()
