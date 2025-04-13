from playwright.sync_api import sync_playwright
import time
import os
print("Lưu cookie tại:", os.path.abspath("cookies.json"))
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    page = context.new_page()
    page.goto("https://wholesale.powercallair.com/tm/tmLogin.lts")

    # Điền form (update username và password thiệt vào đây)
    page.fill('input[name="user_agt_Code"]', "5253")
    page.fill('input[name="user_id"]', "HANVIETAIR")
    page.fill('input[name="user_password"]', "Ha@112233")
    # Click nút Login (dựa trên class hoặc text)
    page.click('span[id="loginSubmit"]')  # hoặc dùng text nếu có: page.click("text=Login")

    # Chờ redirect hoặc trang sau khi login xong
    page.wait_for_load_state("networkidle")

    # In URL sau khi login xong
    print("Login OK, đang ở:", page.url)
    time.sleep(5)
    # Bây giờ vẫn giữ nguyên session => có thể truy cập trang khác
     # Ví dụ
    print("Đã truy cập vào trang chính:", page.url)

    # Nếu muốn giữ session để lần sau dùng => lưu cookies
    cookies = context.cookies()
    import json
    with open("cookies.json", "w") as f:
        json.dump(cookies, f)

  
    