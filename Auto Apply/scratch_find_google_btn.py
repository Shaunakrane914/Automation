import time
from playwright.sync_api import sync_playwright

CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE_DIR = r"C:\Users\Shaunak Rane\Desktop\Projects\Automation\Auto Apply\chrome_profile_persistent"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        executable_path=CHROME_EXE,
        headless=False,
        args=["--start-maximized"]
    )
    page = context.pages[0]
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded")
    time.sleep(3)

    btns = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('button, a, div[role=\"button\"], span'))
            .map(e => ({
                tag: e.tagName,
                text: (e.innerText || '').trim(),
                id: e.id,
                role: e.getAttribute('role'),
                dataTestId: e.getAttribute('data-testid'),
                href: e.href || ''
            }))
            .filter(e => e.text.toLowerCase().includes('google') || (e.id && e.id.includes('google')) || (e.dataTestId && e.dataTestId.includes('google')));
    }""")
    print("Found Google matching elements:")
    for b in btns:
        print(b)

    context.close()
