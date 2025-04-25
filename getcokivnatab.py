import pychrome
import time

def wait_until_input_ready(tab, timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        res = tab.call_method("Runtime.evaluate", expression='''
            !!document.querySelector("input[name='username']")
        ''')
        if res.get("result", {}).get("value"):
            return True
        time.sleep(0.5)
    return False

# Kết nối Chrome DevTools
browser = pychrome.Browser(url="http://127.0.0.1:9222")
tab = browser.new_tab()
tab.start()

# Enable các domain
tab.call_method("Page.enable")
tab.call_method("DOM.enable")
tab.call_method("Runtime.enable")

# Navigate tới trang login
tab.call_method("Page.navigate", url="https://tap.vietnamairlines.com/login")
input()
# Đợi form hiện ra
cookies = tab.call_method("Network.getAllCookies")["cookies"]

# Lưu vào file JSON
import json
with open("tabcookies.json", "w", encoding="utf-8") as f:
    json.dump(cookies, f, indent=2)