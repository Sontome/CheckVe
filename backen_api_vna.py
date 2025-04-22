import aiohttp
import json
import asyncio
from datetime import datetime
import os
import subprocess
CONFIG_GIA_FILE = "config_gia_vna.json"

# 🔧 Giá mặc định
DEFAULT_CONFIG_GIA = {
   
    "PHI_XUAT_VE_1CH": 30000,
    "PHI_XUAT_VE_2CH": 10000
}
def load_cookie_from_state():
    with open(COOKIE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)
        cookies = {cookie["name"]: cookie["value"] for cookie in state["cookies"]}
        return cookies
def is_json_response(resp):
    try:
        resp.json()
        return True
    except Exception:
        return False
# 📦 Load cấu hình giá
def load_config_gia():
    if os.path.exists(CONFIG_GIA_FILE):
        try:
            with open(CONFIG_GIA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config_loaded = {
                    "PHI_XUAT_VE_1CH": int(data.get("PHI_XUAT_VE_1CH", DEFAULT_CONFIG_GIA["PHI_XUAT_VE_1CH"])),
                    "PHI_XUAT_VE_2CH": int(data.get("PHI_XUAT_VE_2CH", DEFAULT_CONFIG_GIA["PHI_XUAT_VE_2CH"]))
                }

                # 🖨️ In ra log
                print("📥 Đã load cấu hình giá từ file:")
                for key, value in config_loaded.items():
                    print(f"  - {key}: {value:,}đ")

                
                return config_loaded
        except Exception as e:
            print("❌ Lỗi khi đọc config_gia.json:", e)

    print("⚠️ Không tìm thấy hoặc lỗi file config_gia.json, dùng mặc định:")
    for key, value in DEFAULT_CONFIG_GIA.items():
        print(f"  - {key}: {value:,}đ")

    
    return DEFAULT_CONFIG_GIA.copy()
config_gia = load_config_gia()
def price_add(sochieu, config_gia: dict) -> int:
    tong = 0

    # 👕 Hành lý chiều đi
    if str(sochieu)=="2" :
        tong += config_gia["PHI_XUAT_VE_2CH"]
    else:
        tong += config_gia["PHI_XUAT_VE_1CH"]



    return tong
def format_time(time_int):
    time_str = str(time_int).zfill(4)  # Thêm số 0 ở đầu cho đủ 4 số
    return f"{time_str[:2]}:{time_str[2:]}"

def to_price(price):
    rounded = round(price / 100) * 100  # Làm tròn đến hàng trăm
    str_price = f"{rounded:,}".replace(",", ".")  # Đổi dấu ',' thành dấu '.'
    return f"{str_price}w"

def format_date(ngay_str):
    if "-" in ngay_str and len(ngay_str) == 10:
        # Trường hợp "2025-04-22" => "20250422"
        return ngay_str.replace("-", "")
    elif len(ngay_str) == 8:
        # Trường hợp "20250422" => "22/04"
        return f"{ngay_str[6:8]}/{ngay_str[4:6]}"
    else:
        print("ngày tháng không đúng định dạng")
        return None
def create_session_powercall():
    now = datetime.now()
    # Format kiểu: yyyyMMdd_HHmmss, ví dụ: 20250418_221530
    session_str = now.strftime("%Y%m%d_%H%M%S")
    return session_str
async def doc_va_loc_ve_re_nhat(data, session, headers, form_data,session_goc):
    fares = data.get("FARES", [])

    def loc_fare_vn(fare):
        return fare.get("IT") == "VFR" and fare.get("CA") == "VN" and fare.get("VA") == "0"

    def loc_fare_vn_noituyen(fare):
        return fare.get("IT") == "VFR" and fare.get("CA") == "VN" and fare.get("VA") == "1"

    # Nếu chưa có vé thì call lại API
    if not fares:
        print("ko thấy dữ liệu chuyến bay >  recheck")

        async with session.post(
            "https://wholesale.powercallair.com/booking/findSkdFareGroup.lts?viewType=xml",
            headers=headers,
            data=form_data
        ) as response:
            if response.status != 200:
                print("ko call được API, mã lỗi:", response.status)
                return None

            try:
                result = await response.text()
                data = json.loads(result)
                fares = data.get("FARES", [])

                if not fares:
                    print("Hết vé chiều đi hoặc chiều về, đổi ngày bay 🥲")
                    return None

            except json.JSONDecodeError:
                print("API trả về không phải json, check lỗi cookie, không parse được JSON")
                return None

    # 👉 Lọc vé phù hợp
    fares_chinh = list(filter(loc_fare_vn, fares))
    fares_phu = list(filter(loc_fare_vn_noituyen, fares))
    
    with open("./va0.json", "w", encoding="utf-8") as f:
                                json.dump(fares_chinh, f, ensure_ascii=False, indent=4)
    with open("./va1.json", "w", encoding="utf-8") as f:
                                json.dump(fares_phu, f, ensure_ascii=False, indent=4)
    if fares_chinh:
        cheapest = min(fares_chinh, key=lambda fare: int(fare.get("MA", 999999999)))
        return cheapest
    elif fares_phu:
        cheapest = min(fares_phu, key=lambda fare: int(fare.get("MA", 999999999)))
        return cheapest
    else:
        print("Không có vé phù hợp điều kiện VN + VFR 🥲")
        return None
def thong_tin_ve(data, sochieu, name):
    if not data:
        return "❌ Không có dữ liệu vé!"

    hang = "Vietnam Airlines"
    
    chang_bay = data.get("AP", "??-??")
    va = data.get("VA")
    print(va)
    if str(va) == "0" : 
        kieubay = "Bay Thẳng"
    else : 
        kieubay = "Nối Tuyến"
    chieu_text = "1 Chiều" if str(sochieu) == "1" else "Khứ hồi"

    sk = data.get("SK", [])
    thongtin_chang = ""
    for s in sk:
        ga_di = s.get("DA", "??")
        ga_den = s.get("AA", "??")
        try : 
            ga_noi= s.get("VA1", "??")
            if ga_noi !="??":
                gio_di = format_time(s.get("DT", 0))
                ngay_di = format_date(str(s.get("DD", "")))
                thongtin_chang += f"\n {ga_di}-{ga_noi}-{ga_den} {gio_di} ngày {ngay_di}"
            else:
                gio_di = format_time(s.get("DT", 0))
                ngay_di = format_date(str(s.get("DD", "")))
                thongtin_chang += f"\n {ga_di}-{ga_den} {gio_di} ngày {ngay_di}"
        except:
            gio_di = format_time(s.get("DT", 0))
            ngay_di = format_date(str(s.get("DD", "")))
            thongtin_chang += f"\n {ga_di}-{ga_den} {gio_di} ngày {ngay_di}"

    # Hành lý cơ bản
    hanhly_xachtay = "12kg"
    hanhly_kygui = "46kg"

    gia_ve = data.get("MA", 0)+price_add(sochieu,config_gia)

    # 👉 Format giá vé
    gia_str = to_price(gia_ve)

    return f"""👤 Tên Khách: {name}

 Hãng: {hang} - Chặng bay: {chang_bay} | {chieu_text} ( {kieubay} )  
{thongtin_chang}

 {hang} {hanhly_xachtay} xách tay, {hanhly_kygui} ký gửi, giá vé = {gia_str}
 
"""
async def get_vna_flight_options(
    
    trip,
    dep0,
    arr0,
    depdate0,
    depdate1,
    retdate,
    sochieu,
    
    
):
    with open("statevna.json", "r", encoding="utf-8") as f:
        raw_cookies = json.load(f)["cookies"]

    cookies = {cookie["name"]: cookie["value"] for cookie in raw_cookies}
    sesion_powercall=create_session_powercall()
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
        
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-ch-ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-csrf-token": "",
        "x-requested-with": "XMLHttpRequest"
        
    }

    
    form_data= {
         "mode": "v3",
       
        'trip': trip,
        "dayInd": "N",
        "strDateSearch": "202504",
       
        "plusDate": "",
        "daySeq": "0",
        'dep0': dep0,
        'dep1': arr0,
       
        'arr0': arr0,
        'arr1': dep0,
       
        'depdate0': depdate0,
        'depdate1': depdate1,
       
        'retdate': retdate,
        
        "comp": "Y",
        "adt": "1",
        "chd": "0",
        "inf": "0",
        "car": "YY",
        "idt": "ALL",
        "isBfm": "Y",
        "CBFare": "YY",
        "skipFilter": "Y",
        "miniFares": "Y",
         "sessionKey": sesion_powercall
    }
    if dep0 not in ["PUS", "ICN"]:
        form_data["arr1"] = ""
        
    if sochieu==1 :
       
        form_data["trip"] ="OW"
        form_data["dep1"] =""
        
        form_data["depdate1"] =""
        
        form_data["retdate"] =""

    
    
    connector = aiohttp.TCPConnector(ssl=False)
    async with aiohttp.ClientSession(cookies=cookies,connector=connector) as session:
        async with session.post("https://wholesale.powercallair.com/booking/findSkdFareGroup.lts?viewType=xml", headers=headers, data=form_data) as responsevna:
            if responsevna.status != 200:
                print("ko gọi được API, mã lỗi:", responsevna.status)
                return None

            resultvna = await responsevna.text()
            if not is_json_response(responsevna):
                
                file_path = "./test.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(resultvna, f, ensure_ascii=False, indent=4)
                print("API trả về không phải json, khả năng sai cookie, không parse được JSON")
                return None


            try:
                datavna = json.loads(resultvna)
                file_path = "./test.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(datavna, f, ensure_ascii=False, indent=4)
                session_goc = datavna.get("SessionKey")
                print(session_goc)
                form_data= {
                    "mode": "v3",
                    'activedCar' : "KE,7C,ZH,VJ,VN,NX,OZ,MU,CZ,MH",
                    'activedCLSS1' : 'Q,S,T,V,E,A,N,H,B,Y,P,Z,R,M',
                    'activedCLSS2' : 'L,Z,V,H,B,Y,W,U,P,S,N',
                    'activedAirport' :'{dep0}-{arr0}-{arr0}-{dep0}',
                    'activedVia':0,
                    'activedStatus' : 'OK,HL',
                    'activedIDT': 'ADT,VFR,LBR',
                    'minAirFareView': '10000',
                    'maxAirFareView': '2000000',
                    'page': '1',
                    'sort': 'priceAsc',
                    'interval01Val': '1310',
                    'interval02Val': '1135',
                    'filterTimeSlideMin0': '10',
                    'filterTimeSlideMax0': '2045',
                    'filterTimeSlideMin1': '45',
                    'filterTimeSlideMax1': '2345',
                    'trip': trip,
                    "dayInd": "N",
                    "strDateSearch": "202504",
                
                    "plusDate": "",
                    "daySeq": "0",
                    'dep0': dep0,
                    'dep1': arr0,
                
                    'arr0': arr0,
                    'arr1': dep0,
                
                    'depdate0': depdate0,
                    'depdate1': depdate1,
                
                    'retdate': retdate,
                    
                    "comp": "Y",
                    "adt": "1",
                    "chd": "0",
                    "inf": "0",
                    "car": "YY",
                    "idt": "ALL",
                    "isBfm": "Y",
                    "CBFare": "YY",
                    "skipFilter": "Y",
                    "miniFares": "Y",
                    "sessionKey": session_goc
                }
                headers = {
                    "accept": "application/json, text/javascript, */*; q=0.01",
                    "accept-language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": "\"Windows\"",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "x-csrf-token": "",
                    "x-requested-with": "XMLHttpRequest"
                }
                async with session.post("https://wholesale.powercallair.com/booking/findSkdFareGroup.lts?viewType=xml", headers=headers, data=form_data) as responsevna:
                    # resultvna = await responsevna.text()
                    # print('goilan 2')
                    # print(form_data)
                    # datavna = json.loads(resultvna)



                    # file_path = "./test1.json"
                    # with open(file_path, "w", encoding="utf-8") as f:
                    #     json.dump(datavna, f, ensure_ascii=False, indent=4)
                    

                    return await doc_va_loc_ve_re_nhat(datavna, session, headers, form_data,session_goc)
            except json.JSONDecodeError:
                file_path = "./test.json"
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(resultvna, f, ensure_ascii=False, indent=4)
                print("API trả về không phải json, khả năng sai cookie, không parse được JSON")
                return None

# Đổi tên hàm thành api_vna cho đúng bài
async def api_vna(
    
    
    dep0,
    arr0,
    depdate0,
    depdate1="",
    
    name="khách lẻ",
    sochieu="1"
):
    # Nếu chưa truyền depdate1 thì auto gán bằng retdate
    trip = "RT"
    if str(sochieu) == "1":
            depdate1=""
            trip = "OW"
    print(f"🛫 Tìm vé cho: {name} | Số chiều: {sochieu}")
    print(f"From {dep0} to {arr0} | Ngày đi: {depdate0} | Ngày về: {depdate1 if trip == 'RT' else '⛔ Không có'}")
    
        
    resultvna = await get_vna_flight_options(
        
        trip=trip,
        dep0=dep0,
        arr0=arr0,
        depdate0=format_date(depdate0),
        depdate1=format_date(depdate1),
        retdate=format_date(depdate1),
        sochieu=sochieu
    )
    thongtin = thong_tin_ve(resultvna,sochieu,name)
    print( thongtin)
    return thongtin

