import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent",
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=False,
        viewport={"width": 1280, "height": 720}
    )
    page = context.pages[0]
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded")
    time.sleep(4)

    print("Triggering click via JavaScript...")
    res = page.evaluate("""() => {
        const btn = Array.from(document.querySelectorAll('*'))
            .find(e => e.innerText && e.innerText.trim() === 'Continue with Google');
        if (btn) {
            btn.click();
            return 'CLICKED: ' + btn.tagName;
        }
        return 'NOT FOUND';
    }""")
    print("JS Click Result:", res)
    time.sleep(5)
    print("URL after 5s:", page.url)
    print("All page URLs in context:", [p.url for p in context.pages])
    context.close()
