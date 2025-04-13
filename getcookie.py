from playwright.sync_api import sync_playwright
import json
import time
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    # Load lại cookies
    with open("cookies.json", "r") as f:
        cookies = json.load(f)
    context.add_cookies(cookies)

    page = context.new_page()
    page.goto("https://wholesale.powercallair.com/b2bIndex.lts")
    print("Đang ở:", page.url)
    time.sleep (10000)











time.sleep (10000)
