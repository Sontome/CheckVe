import pychrome
import time
import json

with open("tabcookies.json", "r", encoding="utf-8") as f:
    cookies = json.load(f)
browser = pychrome.Browser(url="http://127.0.0.1:9222")
tab = browser.new_tab()
tab.start() 
# Enable Network trước khi set
tab.call_method("Page.navigate", url="https://tap.vietnamairlines.com/booking")
tab.call_method("Network.enable")

# Set từng cookie
for cookie in cookies:
    tab.call_method("Network.setCookie", **{
        "name": cookie["name"],
        "value": cookie["value"],
        "domain": cookie["domain"],
        "path": cookie["path"],
        "expires": cookie.get("expires", -1),
        "httpOnly": cookie.get("httpOnly", False),
        "secure": cookie.get("secure", False),
        "sameSite": cookie.get("sameSite", "None")
    })

# Rồi mới navigate

# Giữ tab mở để quan sát
time.sleep(11111)