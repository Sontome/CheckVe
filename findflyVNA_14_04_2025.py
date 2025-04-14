from playwright.sync_api import sync_playwright
import os
import requests
import json

def load_cookies_from_playwright(file_path):
    with open(file_path, 'r') as f:
        storage = json.load(f)

    cookies = {}
    for cookie in storage['cookies']:
        if 'powercallair.com' in cookie['domain']:
            cookies[cookie['name']] = cookie['value']
    return cookies

def fetch_fare_group():
    url = "https://wholesale.powercallair.com/booking/findSkdFareGroup.lts?viewType=xml"

    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-csrf-token": "",  # Nếu có token thật thì thay vào đây
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://wholesale.powercallair.com/booking/findSkdFareGroup.lts?mode=v3",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"
    }

    # Body dạng x-www-form-urlencoded
    payload = {
        "qcars": "",
        "mode": "v3",
        "activedCar": "VN",
        "activedCLSS1": "K,Y,M,T,L,N,O,S,B,W,V",
        "activedCLSS2": "K,H,J,O,N,L,S,Q,B,Y,R,M",
        "activedAirport": "ICN-DAD-DAD-ICN",
        "activedVia": "0",
        "activedStatus": "OK,HL",
        "activedIDT": "ADT,VFR",
        "minAirFareView": "380400",
        "maxAirFareView": "1415700",
        "page": "1",
        "sort": "priceAsc",
        "interval01Val": "1170",
        "interval02Val": "1080",
        "filterTimeSlideMin0": "650",
        "filterTimeSlideMax0": "2155",
        "filterTimeSlideMin1": "5",
        "filterTimeSlideMax1": "2340",
        "trip": "RT",
        "dayInd": "N",
        "strDateSearch": "202504",
        "day": "",
        "plusDate": "",
        "daySeq": "0",
        "dep0": "ICN",
        "dep1": "DAD",
        "dep2": "",
        "dep3": "",
        "arr0": "DAD",
        "arr1": "ICN",
        "arr2": "",
        "arr3": "",
        "depdate0": "20250415",
        "depdate1": "20250415",
        "depdate2": "",
        "depdate3": "",
        "retdate": "20250415",
        "val": "",
        "comp": "Y",
        "adt": "1",
        "chd": "0",
        "inf": "0",
        "car": "YY",
        "idt": "ALL",
        "isBfm": "Y",
        "CBFare": "YY",
        "skipFilter": "",
        "miniFares": "Y",
        "sessionKey": "LUWCHB6HV3LNBUOY2WT9"
    }

    # Load cookies từ file playwright nếu cần
    cookies = load_cookies_from_playwright("pc_login.json")

    response = requests.post(url, headers=headers, data=payload, cookies=cookies)

    # Lưu kết quả vào file
    with open("fare_filtered.json", "w", encoding="utf-8") as f:
        f.write(response.text)

    print("✅ Done, đã lưu file JSON: fare_filtered.json")




#fetch_fare_group()
def find_cheapest_fare(input_file="fare_filtered.json", output_file="no1fly.json"):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        fares = data.get("FARES", [])
        if not fares:
            print("Không có dữ liệu FARES trong file.")
            return

        # Lọc vé có XA là số nguyên, loại vé nào thiếu XA hoặc sai kiểu
        valid_fares = [fare for fare in fares if str(fare.get("XA", "")).isdigit()]

        if not valid_fares:
            print("Không tìm được vé nào có XA hợp lệ.")
            return

        # Chuyển XA về int để so sánh
        cheapest = min(valid_fares, key=lambda x: int(x["XA"]))

        # Ghi object rẻ nhất vào file
        with open(output_file, "w", encoding="utf-8") as f_out:
            json.dump(cheapest, f_out, ensure_ascii=False, indent=2)

        print(f"✅ Đã lưu vé rẻ nhất vào '{output_file}': XA = {cheapest['XA']}")
    
    except Exception as e:
        print(f"❌ Lỗi: {e}")

# Gọi hàm liền tay
find_cheapest_fare()

