import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch()
    page = b.new_page()
    page.goto("https://in.indeed.com/account/login", wait_until="domcontentloaded")
    time.sleep(5)
    html = page.evaluate("""() => {
        const el = document.querySelector('#button-label');
        if (!el) return 'NO #button-label after 5s';
        let curr = el;
        let res = [];
        for (let i = 0; i < 4; i++) {
            if (curr) {
                res.push({ tag: curr.tagName, id: curr.id, className: curr.className, html: curr.outerHTML.substring(0, 150) });
                curr = curr.parentElement;
            }
        }
        return res;
    }""")
    print("Hierarchy after 5s:", html)
    b.close()
