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

    info = page.evaluate("""() => {
        const el = document.elementFromPoint(632, 366);
        return {
            tag: el ? el.tagName : null,
            id: el ? el.id : null,
            className: el ? el.className : null,
            text: el ? el.innerText : null,
            outerHTML: el ? el.outerHTML.substring(0, 200) : null
        };
    }""")
    print("Element at (632, 366) in persistent Chrome:", info)
    context.close()
