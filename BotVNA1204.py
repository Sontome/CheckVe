import time
import os
from PIL import Image
from io import BytesIO
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
CONFIG = {
    'SCOPES': ['https://www.googleapis.com/auth/spreadsheets'],
    'SERVICE_ACCOUNT_FILE': 'keysheetvna.json',  # File credentials của bạn
    'SPREADSHEET_ID': '1RyL5_rm7wFyR6VPpOl2WrsgFjbz2m1cNtATXR7DK190',
    'TELEGRAM_BOT_TOKEN': '7579394048:AAE8W83TfxHemGzMXvOLUhQheXNRCh1InsA',
    'TELEGRAM_CHAT_ID': str(-4622194613),  # room tele chính
    
}




CONFIGTEST = {
    'SCOPES': ['https://www.googleapis.com/auth/spreadsheets'],
    'SERVICE_ACCOUNT_FILE': 'keytest.json',  # File credentials của bạn
    'SPREADSHEET_ID': '1OwKfz3bhJKai2ph6Fc8GOeN087hBU1jPY9dm02ZisQo',
    'TELEGRAM_BOT_TOKEN': '7579394048:AAE8W83TfxHemGzMXvOLUhQheXNRCh1InsA',
    'TELEGRAM_CHAT_ID': str(-4698930772),  # room tele chính
    
}

#CONFIG=CONFIGTEST



TELEGRAM_API_URL = f'https://api.telegram.org/bot{CONFIG["TELEGRAM_BOT_TOKEN"]}/sendMessage'
bot_token = CONFIG['TELEGRAM_BOT_TOKEN']
chat_id = CONFIG['TELEGRAM_CHAT_ID']
driver = None
CONFIG_GIA_FILE = "config_gia_vna.json"

# 🔧 Giá mặc định
DEFAULT_CONFIG_GIA = {
    "1_CHIEU": 30000,
    "2_CHIEU": 20000,
    "USER_POWERCALL": '5253',
    "PW_POWERCALL": 'Ha@112233',
}

# 📦 Load cấu hình giá
def load_config_gia():
    if os.path.exists(CONFIG_GIA_FILE):
        try:
            with open(CONFIG_GIA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config_loaded = {
                    "1_CHIEU": int(data.get("1_CHIEU", DEFAULT_CONFIG_GIA["1_CHIEU"])),
                    "2_CHIEU": int(data.get("2_CHIEU", DEFAULT_CONFIG_GIA["2_CHIEU"])),
                    "USER_POWERCALL": str(data.get("USER_POWERCALL", DEFAULT_CONFIG_GIA["USER_POWERCALL"])),
                    "PW_POWERCALL": str(data.get("PW_POWERCALL", DEFAULT_CONFIG_GIA["PW_POWERCALL"]))
                    
                }

                # 🖨️ In ra log
                print("📥 Đã load cấu hình giá từ file:")
                for key, value in config_loaded.items():
                    print(f"  - {key}: {value:}")

                input("⏸️ Ấn Enter để tiếp tục...")
                return config_loaded
        except Exception as e:
            print("❌ Lỗi khi đọc config_gia_vna.json:", e)

    print("⚠️ Không tìm thấy hoặc lỗi file config_gia_vna.json, dùng mặc định:")
    for key, value in DEFAULT_CONFIG_GIA.items():
        print(f"  - {key}: {value:}")

    input("⏸️ Ấn Enter để tiếp tục...")
    return DEFAULT_CONFIG_GIA.copy()

# 💾 Lưu config
def save_config_gia(config):
    with open(CONFIG_GIA_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    print("✅ Đã lưu cấu hình giá mới!")

# 📲 Nhập thủ công
def update_config_gia(config):
    print("\n🎛️ Cấu hình giá hiện tại:")
    for key, val in config.items():
        print(f"- {key}: {val}")

    print("\n💬 Nhập giá mới (Enter để giữ nguyên):")

    for key in config:
        val = input(f"{key} [{config[key]}]: ").strip()
        if val:
            try:
                config[key] = int(val)
            except ValueError:
                print("⚠️ Không hợp lệ, giữ nguyên.")

    return config
CONFIG_VNA = load_config_gia()

usernameVNA = CONFIG_VNA["USER_POWERCALL"]
passwordVNA = CONFIG_VNA["PW_POWERCALL"]



def giacuoi(sochieu):
    if sochieu == "1_CHIEU":
        tong = CONFIG_VNA["1_CHIEU"]
    elif sochieu == "2_CHIEU":
        tong = CONFIG_VNA["2_CHIEU"]

    # Tính phí hành lý
    

    # Tính phí xuất vé
    

    return tong
def send_telegram(message, bot_token=None, chat_id=None, driver=None, element=None, send_photo=True, img_path="fullVNA.png"):
    """
    Gửi tin nhắn Telegram:
    - send_photo = True → gửi ảnh kèm (ưu tiên element nếu có)
    - img_path → tuỳ chọn tên file ảnh (mặc định: fullVNA.png)
    👉 Trả về (success: bool, message_id: int hoặc None)
    """
    if not bot_token or not chat_id:
        raise ValueError("bot_token và chat_id là bắt buộc")

    data = {
        'chat_id': chat_id,
        'parse_mode': 'HTML',
    }

    try:
        if send_photo and (driver or element):
            # Chụp ảnh theo element hoặc toàn trình duyệt
            if element:
                element.screenshot(img_path)
            elif driver:
                driver.save_screenshot(img_path)

            with open(img_path, 'rb') as f:
                files = {
                    'photo': (os.path.basename(img_path), f)
                }
                data['caption'] = message

                response = requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendPhoto",
                    data=data,
                    files=files
                )

            os.remove(img_path)

        else:
            # Gửi tin nhắn chữ
            data['text'] = message
            response = requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                data=data
            )

        if response.status_code == 200:
            res_json = response.json()
            return True, res_json.get("result", {}).get("message_id")
        else:
            print("❌ Gửi lỗi :", response.text)
            return False, None

    except Exception as e:
        print(f"❌ Lỗi khi gửi Telegram: {e}")
        return False, None
send_telegram("Bot VNA : On", bot_token=bot_token, chat_id=chat_id)        
def cut_year(date_str: str, simple: bool = False) -> str:
    """
    - Nếu `simple=False` (default): 'HH:MM ngày DD/MM/YYYY' → 'HH:MM ngày DD/MM'
    - Nếu `simple=True`: 'YYYY/MM/DD' → 'DD/MM'
    """
    try:
        if simple:
            dt = datetime.strptime(date_str, "%Y/%m/%d")
            return dt.strftime("%d/%m")
        else:
            dt = datetime.strptime(date_str, "%H:%M ngày %d/%m/%Y")
            return dt.strftime("%H:%M ngày %d/%m")
    except ValueError:
        print(f"❌ Format sai: {date_str}")
        return date_str

def to_value(currency_str: str) -> int:
    """
    Nhận chuỗi kiểu '138,300 KRW' => trả về số nguyên 138300
    """
    try:
        clean_str = ''.join(c for c in currency_str if c.isdigit())
        return int(clean_str)
    except:
        print(f"❌ Không parse được: {currency_str}")
        return 0

def to_price(amount: int, currency: str = "w", round_to: int = 100) -> str:
    """
    Chuyển số nguyên thành chuỗi kiểu '1,138,300 KRW'
    Làm tròn đến gần nhất round_to (mặc định 100)
    """
    try:
        # Làm tròn đến gần nhất 'round_to'
        rounded = round(amount / round_to) * round_to
        formatted = f"{rounded:,}".replace(",", ".")
        return f"{formatted}{currency}"
    except:
        print(f"❌ Không convert được: {amount}")
        return str(amount)

def setup_chrome_driver():
    """
    Thiết lập và khởi động ChromeDriver
    :return: Đối tượng WebDriver
    """
    try:
        # Thiết lập options cho Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Chạy ẩn (bỏ comment nếu muốn chạy ẩn)
        
        chrome_options.add_argument("--window-size=1080,760")
        
        # Khởi tạo service và driver
        
        driver = webdriver.Chrome(options=chrome_options)
        
        print("Đã khởi động ChromeDriver thành công")
        return driver
    except Exception as e:
        print(f"Lỗi khi khởi động ChromeDriver: {str(e)}")
        return None

def close_chrome_driver():
    """
    Đóng ChromeDriver
    """
    global driver
    if driver:
        try:
            driver.quit()
            print("Đã đóng ChromeDriver")
        except Exception as e:
            print(f"Lỗi khi đóng ChromeDriver: {str(e)}")
        finally:
            driver = None


def get_google_sheets_service():
    try:
        # Đọc credentials từ file JSON
        credentials = service_account.Credentials.from_service_account_file(
            CONFIG['SERVICE_ACCOUNT_FILE'], scopes=CONFIG['SCOPES'])
        
        # Tạo service
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except Exception as e:
        print(f"Lỗi khi kết nối đến Google Sheets: {str(e)}")
        return None

def read_sheet(spreadsheet_id, range_name):
    """
    Đọc dữ liệu từ Google Sheet
    :param spreadsheet_id: ID của spreadsheet
    :param range_name: Phạm vi cần đọc (ví dụ: 'Sheet1!A1:D10')
    :return: Dữ liệu từ sheet
    """
    try:
        service = get_google_sheets_service()
        if service:
            sheet = service.spreadsheets()
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            values = result.get('values', [])
            
            return values
        return None
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu: {str(e)}")
        return None

def get_sheet_id(spreadsheet_id, sheet_name):
    """
    Lấy sheetId của một sheet trong bảng tính.
    :param spreadsheet_id: ID của spreadsheet
    :param sheet_name: Tên sheet (ví dụ: 'Hàng Chờ')
    :return: sheetId nếu tìm thấy, None nếu không tìm thấy
    """
    try:
        service = get_google_sheets_service()
        if service:
            # Lấy metadata của bảng tính
            sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            sheets = sheet_metadata.get('sheets', [])
            
            # Tìm sheetId từ tên sheet
            for sheet in sheets:
                if sheet.get('properties', {}).get('title') == sheet_name:
                    return sheet.get('properties', {}).get('sheetId')
            print(f"Không tìm thấy sheet '{sheet_name}' trong bảng tính.")
            return None
        return None
    except Exception as e:
        print(f"Lỗi khi lấy sheetId: {str(e)}")
        return None

def delete_row_by_range(spreadsheet_id, range_name):
    """
    Xóa một hàng trong Google Sheets bằng cách sử dụng range_name.
    :param spreadsheet_id: ID của spreadsheet
    :param range_name: Phạm vi cần xóa (ví dụ: 'Hàng Chờ!A2:Z2')
    """
    try:
        service = get_google_sheets_service()
        if service:
            # Lấy sheetId từ tên sheet
            sheet_name = range_name.split('!')[0]
            sheet_id = get_sheet_id(spreadsheet_id, sheet_name)
            if sheet_id is None:
                print(f"Lỗi: Không tìm thấy sheetId cho sheet '{sheet_name}'")
                return None

            # Phân tích phạm vi
            range_parts = range_name.split('!')[1]
            col_start = range_parts.split(':')[0][0]  # Cột bắt đầu
            row_start = int(range_parts.split(':')[0][1:]) - 1  # Hàng bắt đầu (chuyển sang chỉ số 0)
            col_end = range_parts.split(':')[1][0]  # Cột kết thúc
            row_end = int(range_parts.split(':')[1][1:])  # Hàng kết thúc (không cần chuyển đổi)

            # Kiểm tra xem phạm vi có xóa đúng 1 hàng hay không
            if row_start != row_end - 1:
                print("Phạm vi không phải là một hàng duy nhất.")
                return None

            # Tạo yêu cầu để xóa hàng
            batch_update_request = {
                "requests": [
                    {
                        "deleteRange": {
                            "range": {
                                "sheetId": sheet_id,  # Sử dụng sheetId ở đây
                                "startRowIndex": row_start,
                                "endRowIndex": row_end
                            },
                            "shiftDimension": "ROWS"
                        }
                    }
                ]
            }
            
            # Gửi yêu cầu xóa hàng
            sheet = service.spreadsheets()
            response = sheet.batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=batch_update_request
            ).execute()
            print(f"Đã xóa hàng trong phạm vi {range_name} thành công.")
            return response
        return None
    except Exception as e:
        print(f"Lỗi khi xóa hàng: {str(e)}")
        return None

def update_sheet(spreadsheet_id, range_name, values):
    """
    Cập nhật dữ liệu trong Google Sheet
    :param spreadsheet_id: ID của spreadsheet
    :param range_name: Phạm vi cần cập nhật (ví dụ: 'Sheet1!A1:D10')
    :param values: Giá trị mới để cập nhật (dạng danh sách các danh sách)
    :return: True nếu thành công, False nếu thất bại
    """
    try:
        service = get_google_sheets_service()
        if service:
            sheet = service.spreadsheets()
            body = {
                'values': values
            }
            result = sheet.values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',  # 'RAW' có thể được thay bằng 'USER_ENTERED' nếu cần format
                body=body
            ).execute()
            print(f"Đã cập nhật dữ liệu trong phạm vi {range_name}")
            return True
        return False
    except Exception as e:
        print(f"Lỗi khi cập nhật dữ liệu: {str(e)}")
        return False
def checkVNA2chieu(data, spreadsheet_id):
    global driver
    global usernameVNA
    global passwordVNA
    subuser= 'HANVIETAIR'
    print("Đang xử lý dữ liệu VNA 2 chiều ...")
    
    # Kiểm tra nếu driver chưa được khởi tạo
    if not driver:
        driver = setup_chrome_driver()
        if not driver:
            print("Không thể khởi động ChromeDriver cho VNA")
            return
    
    # TODO: Thêm logic xử lý dữ liệu VJ ở đây
    # Ví dụ: Mở trang web và xử lý dữ liệu
    try:
        # Mở trang web (thay thế URL bằng trang web thực tế)
        driver.get("https://wholesale.powercallair.com/tm/tmLogin.lts")
        print("Đã mở trang web cho VNA")
        
        print(f"Đang nhập username: {usernameVNA}")
        
        # Đợi cho element input username xuất hiện
        wait = WebDriverWait(driver, 15)
        for field_name, value in [("user_agt_Code", usernameVNA), ("user_password", passwordVNA),("user_id", subuser)]:
            input_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"input[name='{field_name}']")))
            input_elem.clear()
            input_elem.send_keys(value)

        # Enter sau khi nhập xong password
        input_elem.send_keys(Keys.RETURN)
        print(f"✅ Đã nhập username: {usernameVNA} và nhấn Enter")
    except:
        print("Lỗi login")
    for row in data:
        wait = WebDriverWait(driver, 20)
        
        print("2 Chiều")
        try:

            try: #chọn nơi đi đến ( nếu từ nước ngoài thì except)
                start = wait.until(
                    EC.presence_of_element_located((By.ID, "dep0"))
                )
                Select(start).select_by_value(row[0])
                start = wait.until(
                    EC.presence_of_element_located((By.ID, "arr1"))
                )
                Select(start).select_by_value(row[0])
                print(f"🛬 Chọn sân bay đi: {row[0]}")
                # Mở city popup
                driver.find_element(By.ID, "arr0_text").click()

                # Log cho vui
                print(f"🛬 Chọn sân bay đến: {row[1]}")

                # Đợi label xuất hiện và click bằng JavaScript
                try:
                    label = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f"label[for='{row[1]}']"))
                    )
                    driver.execute_script("arguments[0].click();", label)

                except Exception as e:
                    print(f"❌ Không chọn được city {row[1]}: {e}")
                    message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n\nHãng: VNA - Chặng bay: "+row[0]+"-"+row[1]+" Khứ Hồi ( Hết Vé )\n\n "
                    
                    message += "<b>Trang web không hỗ trợ chặng đầu hoặc cuối, hãy đổi chặng bay khác </b>"
                    
                    print(message)
                    send_telegram(message, bot_token=bot_token, chat_id=chat_id)
                    break

                
                startdate = datetime.strptime(row[3] , "%m/%d/%Y").strftime("%Y/%m/%d")
                print(f"📅 Ngày đi: {startdate}")

                # Tìm input ngày và set giá trị bằng JavaScript (do readonly)
                date_input = wait.until(
                    EC.presence_of_element_located((By.ID, "depdate0_value"))
                )
                driver.execute_script("arguments[0].value = arguments[1];", date_input, startdate)
                if row[5] == "FALSE": 
                    try:
                        
                        print(" 1 chiều không cần điền ngày về")
                    except Exception as e:
                        print(f"❌ Lỗi khi chờ nút check_OW: {e}")
                    
                    
                else :
                    
                    backdate = datetime.strptime(row[4] , "%m/%d/%Y").strftime("%Y/%m/%d")
                    print(f"📅 Ngày về: {backdate}")

                    # Tìm input ngày và set giá trị bằng JavaScript (do readonly)
                    date_input = wait.until(
                        EC.presence_of_element_located((By.ID, "depdate1_value"))
                    )
                    driver.execute_script("arguments[0].value = arguments[1];", date_input, backdate)
                
            except: 
                print("xuất phát từ nước ngoài")
                checkbox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "areasoto"))
                )
                checkbox.click()
                time.sleep(1)


                start = wait.until(
                    EC.presence_of_element_located((By.ID, "arr0"))
                )
                Select(start).select_by_value(row[1])
                start = wait.until(
                    EC.presence_of_element_located((By.ID, "dep1"))
                )
                Select(start).select_by_value(row[1])
                print(f"🛬 Chọn sân bay đi: {row[0]}")
                # Mở city popup
                driver.find_element(By.ID, "dep0_text").click()

                # Log cho vui
                print(f"🛬 Chọn sân bay đến: {row[1]}")

                # Đợi label xuất hiện và click bằng JavaScript
                try:
                    label = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f"label[for='{row[0]}']"))
                    )
                    driver.execute_script("arguments[0].click();", label)

                except Exception as e:
                    print(f"❌ Không chọn được city {row[0]}: {e}")
                    message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n\nHãng: VNA - Chặng bay: "+row[0]+"-"+row[1]+" Khứ Hồi ( Hết Vé )\n\n "
                    
                    message += "<b>Trang web không hỗ trợ chặng đầu hoặc cuối, hãy đổi chặng bay khác </b>"
                    
                    print(message)
                    send_telegram(message, bot_token=bot_token, chat_id=chat_id)
                    break                    
                
                startdate = datetime.strptime(row[3] , "%m/%d/%Y").strftime("%Y/%m/%d")
                print(f"📅 Ngày đi: {startdate}")

                # Tìm input ngày và set giá trị bằng JavaScript (do readonly)
                date_input = wait.until(
                    EC.presence_of_element_located((By.ID, "depdate0_value"))
                )
                driver.execute_script("arguments[0].value = arguments[1];", date_input, startdate)
                if row[5] == "FALSE": 
                    try:
                        
                        print(" 1 chiều không cần điền ngày về")
                    except Exception as e:
                        print(f"❌ Lỗi khi chờ nút check_OW: {e}")
                    
                    
                else :
                    
                    backdate = datetime.strptime(row[4] , "%m/%d/%Y").strftime("%Y/%m/%d")
                    print(f"📅 Ngày về: {backdate}")

                    # Tìm input ngày và set giá trị bằng JavaScript (do readonly)
                    date_input = wait.until(
                        EC.presence_of_element_located((By.ID, "depdate1_value"))
                    )
                    driver.execute_script("arguments[0].value = arguments[1];", date_input, backdate)

        except:
            print("Trang web không hỗ trợ vé ở điểm đi hoặc điểm tới")
        time.sleep(2)
        driver.execute_script("goSkdFare('L');")


        WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "img[src*='now_waiting12_pwcall.gif']")))
        
        # 1. MỞ MENU HÃNG BAY
        try:
            menu_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#carFilter > a.atHtit'))
            )
            menu_button.click()
        
            # 2. CHỜ PHẦN FILTER HIỆN RA
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#carFilter .carFilter'))
            )

            # 3. CHỜ VÀ CLICK CHỌN VIETNAM AIRLINES
            vn_checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="checkbox"][desc="베트남항공"]'))
            )
        except:
            print('hết vé, chạy hàm báo hết vé all, break')
            message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n\nHãng: VNA - Chặng bay: "+row[0]+"-"+row[1]+" Khứ Hồi ( Hết Vé )\n\n "
            message += row[0]+"-"+row[1]+" ngày "+cut_year(startdate,simple=True)+"\n "
            message += row[1]+"-"+row[0]+" ngày "+cut_year(backdate,simple=True)+"\n"
            message += "<b>Vui Lòng Đổi Ngày Bay Khác </b>"
            print(message)
            driver.save_screenshot("2chieuVNA.png")
            print(message)
            send_telegram(message, bot_token=bot_token, chat_id=chat_id, driver=driver,img_path="2chieuVNA.png")
            break



            
        
        # 4. NẾU CHƯA CHỌN THÌ MỚI CLICK
        if not vn_checkbox.is_selected():
            driver.execute_script("arguments[0].click();", vn_checkbox)
            print("✅ Đã chọn Vietnam Airlines!")
        else:
            print("✅ Vietnam Airlines đã được chọn sẵn rồi!")


        try:
            
        # 1. MỞ MENU VIAFILTER (nếu chưa mở)
            wait.until(EC.invisibility_of_element_located(
                (By.XPATH, "//img[contains(@src, 'now_waiting')]")
            ))
            time.sleep(1)
            print('check vé về thẳng')
            try:
                via_menu_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#viaFilter > a.atHtit'))
                )
                via_menu_button.click()
                time.sleep(1)
                
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "cdk-overlay-backdrop")))
                # 2. CHỜ NÓ HIỆN RA
                
                
                time.sleep(1)
                # 3. TÌM THEO ATTRIBUTE data-text
                label = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="viaFilter"]/div/div/dl/dd[1]/label'))
                )
                driver.execute_script("arguments[0].click();", label)
                time.sleep(1)
                print('click show all lân 1')
                
                
                label = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="viaFilter"]/div/div/dl/dd[2]/label'))
                )
                driver.execute_script("arguments[0].click();", label)  
                time.sleep(1)
                print('click bay thẳng')
                             
                divs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "atLstInt")))
                divs = driver.find_element(By.CLASS_NAME, "atLstInt").click()
                time.sleep(1)
                print("✅ Đã click chuyến bay đầu tiên")
                
                timestart = wait.until(EC.presence_of_element_located((
                    By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[2]/ul/li[2]/ul[1]/li[2]'
                ))).text

                # Lấy thời gian về
                timeback = wait.until(EC.presence_of_element_located((
                    By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[2]/ul/li[2]/ul[2]/li[2]'
                ))).text

                # Lấy giá tiền
                pricetext = wait.until(EC.presence_of_element_located((
                    By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[2]/ul/li[5]/div/strong'
                ))).text
                pricetext = to_price(to_value(pricetext))

                
                el = driver.find_element(By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[3]/div')

                # Scroll tới element cho chắc ăn
                driver.execute_script("arguments[0].scrollIntoView(true);", el)
                time.sleep(2)  # đợi nó render ngon lành

                # Chụp full page trước
                driver.save_screenshot("2ChieuVNAvethang.png")
                giachot = to_value(pricetext) + giacuoi("2_CHIEU")
                # Lấy vị trí & kích thước element
                message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n\nHãng: VNA - Chặng bay: "+row[0]+"-"+row[1]+" Khứ Hồi ( Bay Thẳng )\n\n "
                message += row[0]+"-"+row[1]+ " " + timestart+" ngày "+cut_year(startdate,simple=True)+"\n "
                message += row[1]+"-"+row[0]+ " " + timeback+" ngày "+cut_year(backdate,simple=True)+"\n"
                message += f"<b>Vietnam Airlines 12kg xách tay, 46kg ký gửi, giá vé = {to_price(giachot)}</b>"
                
                
                print(message)
                send_telegram(message, bot_token=bot_token, chat_id=chat_id, driver=driver,img_path="2ChieuVNAvethang.png")
                break


            
                
            

            except:
                print('không có vé về thẳng > check báo vé nối tuyến')






            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "cdk-overlay-backdrop")))
            # 2. CHỜ NÓ HIỆN RA
            
            
            label = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="viaFilter"]/div/div/dl/dd[1]/label'))
            )
            driver.execute_script("arguments[0].click();", label)
            time.sleep(1)
            print('click show all lân 2')
            time.sleep(1)
            
            divs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "atLstInt")))
            time.sleep(2)
            # Click vào thằng đầu tiên
            divs = driver.find_element(By.CLASS_NAME, "atLstInt")

            if divs:
                try:
                    divs.click()
                    print("✅ Đã click chuyến bay đầu tiên")
                    try:
                        noituyendi_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[3]/div/div[1]/div[2]/ul/li[1]/div[2]/span')))
                        
                        noituyendi = noituyendi_element.text
                    except:
                        noituyendi =''
                    if row[5] == "TRUE": 
                        try:    
                            noituyenve_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[3]/div/div[1]/div[4]/ul/li[1]/div[2]/span')))
                            noituyenve = noituyenve_element.text
                        except:
                            noituyenve =''
                    # Lấy thời gian đi
                    timestart = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[2]/ul/li[2]/ul[1]/li[2]'
                    ))).text

                    # Lấy thời gian về
                    if row[5] == "TRUE": 
                        timeback = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[2]/ul/li[2]/ul[2]/li[2]'
                    ))).text

                    # Lấy giá tiền
                    pricetext = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[2]/ul/li[5]/div/strong'
                    ))).text
                    pricetext = to_price(to_value(pricetext))
                    giachot = to_value(pricetext) +giacuoi("2_CHIEU")

                    message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n\nHãng: VNA - Chặng bay: "+row[0]+"-"+row[1]+" Khứ Hồi ( Nối Tuyến )\n\n "
                    # In ra cho chắc
                    
                    
                    
                    
                    if noituyendi==row[1]:
                        message +=  row[0] + "-"+ noituyendi + " " + timestart +" ngày " + cut_year(startdate,simple=True) +"\n "
                    else:
                        message +=  row[0] + "-"+ noituyendi+ "-" +row[1] + " " + timestart +" ngày " + cut_year(startdate,simple=True) +"\n "
                    
                    if noituyenve==row[0]: 
                        message += row[1] + "-"+ noituyenve + " " + timeback +" ngày " + cut_year(backdate,simple=True) +"\n"
                    else:        
                        message += row[1] + "-"+ noituyenve+ "-" +row[0] + " " + timeback +" ngày " + cut_year(backdate,simple=True) +"\n"
                    message += f"<b>Vietnam Airlines 12kg xách tay, 46kg ký gửi, giá vé = {to_price(giachot)}</b>"

                    
                        
                        
                    el = driver.find_element(By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[3]/div')

                    # Scroll tới element cho chắc ăn
                    driver.execute_script("arguments[0].scrollIntoView(true);", el)
                    time.sleep(2)  # đợi nó render ngon lành

                    # Chụp full page trước
                    driver.save_screenshot("2ChieuVNANoituyen.png")

                    # Lấy vị trí & kích thước element
                    
                    send_telegram(message, bot_token=bot_token, chat_id=chat_id, driver=driver,img_path="2ChieuVNANoituyen.png")
                    print(message)
                    break
                    
                except Exception as e:
                    print("❌ Lỗi khi click:", e)
            else:
                print("❌ Hết chuyến bay nối tuyến")
            # 4. CLICK NẾU CHƯA CHỌN
            

            
        except Exception as e:
                print(f" {e}")
            
            
            # 4. Kiểm tra đã được chọn chưa
            
            
    
def checkVNA1chieu(data, spreadsheet_id):
    global driver
    global usernameVNA
    global passwordVNA
    subuser= 'HANVIETAIR'
    print("Đang xử lý dữ liệu VNA 1 chiều ...")
    
    # Kiểm tra nếu driver chưa được khởi tạo
    if not driver:
        driver = setup_chrome_driver()
        if not driver:
            print("Không thể khởi động ChromeDriver cho VNA")
            return
    
    # TODO: Thêm logic xử lý dữ liệu VJ ở đây
    # Ví dụ: Mở trang web và xử lý dữ liệu
    try:
        # Mở trang web (thay thế URL bằng trang web thực tế)
        driver.get("https://wholesale.powercallair.com/tm/tmLogin.lts")
        print("Đã mở trang web cho VNA")
        
        print(f"Đang nhập username: {usernameVNA}")
        
        # Đợi cho element input username xuất hiện
        wait = WebDriverWait(driver, 15)
        for field_name, value in [("user_agt_Code", usernameVNA), ("user_password", passwordVNA),("user_id", subuser)]:
            input_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"input[name='{field_name}']")))
            input_elem.clear()
            input_elem.send_keys(value)

        # Enter sau khi nhập xong password
        input_elem.send_keys(Keys.RETURN)
        print(f"✅ Đã nhập username: {usernameVNA} và nhấn Enter")
    except:
        print("Lỗi login")
    for row in data:
        wait = WebDriverWait(driver, 20)
        
        # Nếu nó đang được check thì click để bỏ chọn
        time.sleep(1)
        print("1 Chiều")
        try:
            try:
                
                start = wait.until(
                    EC.presence_of_element_located((By.ID, "dep0"))
                )


                Select(start).select_by_value(row[0])
                checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "check_OW"))
                )
                time.sleep(1)
                checkbox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "check_OW"))
                )
                checkbox.click()
                print(f"🛬 Chọn sân bay đi: {row[0]}")
                # Mở city popup
                driver.find_element(By.ID, "arr0_text").click()

                # Log cho vui
                print(f"🛬 Chọn sân bay đến: {row[1]}")

                # Đợi label xuất hiện và click bằng JavaScript
                try:
                    label = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f"label[for='{row[1]}']"))
                    )
                    driver.execute_script("arguments[0].click();", label)

                except Exception as e:
                    print(f"❌ Không chọn được city {row[1]}: {e}")
                    message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n\nHãng: VNA - Chặng bay: "+row[0]+"-"+row[1]+" 1 Chiều ( Hết Vé )\n\n "
                    
                    message += "<b>Trang web không hỗ trợ chặng đầu hoặc cuối, hãy đổi chặng bay khác </b>"
                    
                    print(message)
                    send_telegram(message, bot_token=bot_token, chat_id=chat_id)
                    break                    
                
                startdate = datetime.strptime(row[3] , "%m/%d/%Y").strftime("%Y/%m/%d")
                print(f"📅 Ngày đi: {startdate}")

                # Tìm input ngày và set giá trị bằng JavaScript (do readonly)
                date_input = wait.until(
                    EC.presence_of_element_located((By.ID, "depdate0_value"))
                )
                driver.execute_script("arguments[0].value = arguments[1];", date_input, startdate)
            except:
                print('xuat phat từ nước ngoài')
                checkbox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "areasoto"))
                )
                checkbox.click()
                time.sleep(1)
                start = wait.until(
                    EC.presence_of_element_located((By.ID, "arr0"))
                )
                Select(start).select_by_value(row[1])
                checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "check_OW"))
                )
                time.sleep(1)
                checkbox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "check_OW"))
                )
                checkbox.click()
                print(f"🛬 Chọn sân bay đi: {row[0]}")
                # Mở city popup
                driver.find_element(By.ID, "dep0_text").click()

                # Log cho vui
                print(f"🛬 Chọn sân bay đến: {row[1]}")

                # Đợi label xuất hiện và click bằng JavaScript
                try:
                    label = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f"label[for='{row[0]}']"))
                    )
                    driver.execute_script("arguments[0].click();", label)

                except Exception as e:
                    print(f"❌ Không chọn được city {row[1]}: {e}")
                    message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n\nHãng: VNA - Chặng bay: "+row[0]+"-"+row[1]+" 1 Chiều ( Hết Vé )\n\n "
                    
                    message += "<b>Trang web không hỗ trợ chặng đầu hoặc cuối, hãy đổi chặng bay khác </b>"
                    
                    print(message)
                    send_telegram(message, bot_token=bot_token, chat_id=chat_id)
                    break                      
                
                startdate = datetime.strptime(row[3] , "%m/%d/%Y").strftime("%Y/%m/%d")
                print(f"📅 Ngày đi: {startdate}")

                # Tìm input ngày và set giá trị bằng JavaScript (do readonly)
                date_input = wait.until(
                    EC.presence_of_element_located((By.ID, "depdate0_value"))
                )
                driver.execute_script("arguments[0].value = arguments[1];", date_input, startdate)            
            
        except:
            print("Trang web không hỗ trợ vé ở điểm đi hoặc điểm tới")    
        driver.execute_script("goSkdFare('L');")


        WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "img[src*='now_waiting12_pwcall.gif']")))
        
        # 1. MỞ MENU HÃNG BAY
        try:
            menu_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#carFilter > a.atHtit'))
            )
            menu_button.click()
        
            # 2. CHỜ PHẦN FILTER HIỆN RA
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, '#carFilter .carFilter'))
            )

            # 3. CHỜ VÀ CLICK CHỌN VIETNAM AIRLINES
            vn_checkbox = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="checkbox"][desc="베트남항공"]'))
            )
            if not vn_checkbox.is_selected():
                driver.execute_script("arguments[0].click();", vn_checkbox)
                print("✅ Đã chọn Vietnam Airlines!")
            else:
                print("✅ Vietnam Airlines đã được chọn sẵn rồi!")
        except:
            print('hết vé, chạy hàm báo hết vé all, break')
            message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n\nHãng: VNA - Chặng bay: "+row[0]+"-"+row[1]+" 1 Chiều ( Hết Vé )\n\n "
            message += row[0]+"-"+row[1]+" ngày "+cut_year(startdate,simple=True)+"\n"
            
            message += "<b>Vui Lòng Đổi Ngày Bay Khác </b>"
            print(message)
            driver.save_screenshot("1chieuVNA.png")
            print(message)
            send_telegram(message, bot_token=bot_token, chat_id=chat_id, driver=driver,img_path="1chieuVNA.png")
            break



            
        
        # 4. NẾU CHƯA CHỌN THÌ MỚI CLICK
        

        
        try:
            
        # 1. MỞ MENU VIAFILTER (nếu chưa mở)
            wait.until(EC.invisibility_of_element_located(
                (By.XPATH, "//img[contains(@src, 'now_waiting')]")
            ))
            time.sleep(1)
            print('check vé về thẳng')
            try:
                via_menu_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '#viaFilter > a.atHtit'))
                )
                via_menu_button.click()
                time.sleep(1)
                
                wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "cdk-overlay-backdrop")))
                # 2. CHỜ NÓ HIỆN RA
                
                
                time.sleep(1)
                # 3. TÌM THEO ATTRIBUTE data-text
                label = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="viaFilter"]/div/div/dl/dd[1]/label'))
                )
                driver.execute_script("arguments[0].click();", label)
                time.sleep(1)
                print('click show all lân 1')
                
                
                label = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="viaFilter"]/div/div/dl/dd[2]/label'))
                )
                driver.execute_script("arguments[0].click();", label)  
                time.sleep(1)
                print('click bay thẳng')                  
                divs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "atLstInt")))
                divs = driver.find_element(By.CLASS_NAME, "atLstInt").click()
                print("✅ Đã click chuyến bay đầu tiên")
                
                timestart = wait.until(EC.presence_of_element_located((
                    By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[2]/ul/li[2]/ul[1]/li[2]'
                ))).text

                

                # Lấy giá tiền
                pricetext = wait.until(EC.presence_of_element_located((
                    By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[2]/ul/li[5]/div/strong'
                ))).text
                pricetext = to_price(to_value(pricetext))

                
                el = driver.find_element(By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[3]/div')

                # Scroll tới element cho chắc ăn
                driver.execute_script("arguments[0].scrollIntoView(true);", el)
                time.sleep(2)  # đợi nó render ngon lành

                # Chụp full page trước
                driver.save_screenshot("1ChieuVNAvethang.png")
                giachot = to_value(pricetext) +giacuoi("1_CHIEU")
                # Lấy vị trí & kích thước element
                message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n\nHãng: VNA - Chặng bay: "+row[0]+"-"+row[1]+" 1 Chiều ( Bay Thẳng )\n\n "
                message += row[0]+"-"+row[1]+ " " + timestart+" ngày "+cut_year(startdate,simple=True)+"\n"
                
                message += f"<b>Vietnam Airlines 12kg xách tay, 46kg ký gửi, giá vé = {to_price(giachot)}</b>"
                
                
                print(message)
                send_telegram(message, bot_token=bot_token, chat_id=chat_id, driver=driver,img_path="2ChieuVNAvethang.png")
                
                
                break


            
                
            

            except:
                print('không có vé về thẳng > check báo vé nối tuyến')




            
            
            wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "cdk-overlay-backdrop")))
            # 2. CHỜ NÓ HIỆN RA
            
            
            label = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="viaFilter"]/div/div/dl/dd[1]/label'))
            )
            driver.execute_script("arguments[0].click();", label)
            time.sleep(1)
            print('click show all lân 2')
            time.sleep(1)
            divs = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "atLstInt")))
            
            # Click vào thằng đầu tiên
            divs = driver.find_element(By.CLASS_NAME, "atLstInt")

            if divs:
                try:
                    divs.click()
                    time.sleep(1)
                    print("✅ Đã click chuyến bay đầu tiên")
                    
                    noituyendi_element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[3]/div/div[1]/div[2]/ul/li[1]/div[2]/span')))
                    
                    noituyendi = noituyendi_element.text
                    
                    
                    # Lấy thời gian đi
                    timestart = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[2]/ul/li[2]/ul[1]/li[2]'
                    ))).text

                    

                    # Lấy giá tiền
                    pricetext = wait.until(EC.presence_of_element_located((
                        By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[2]/ul/li[5]/div/strong'
                    ))).text
                    pricetext = to_price(to_value(pricetext))
                    giachot = to_value(pricetext) +giacuoi("1_CHIEU")

                    message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n\nHãng: VNA - Chặng bay: "+row[0]+"-"+row[1]+" 1 Chiều ( Nối Tuyến )\n\n "
                    # In ra cho chắc
                    
                    
                    
                    
                    
                    message +=  row[0] + "-"+ noituyendi+ "-" +row[1] + " " + timestart +" ngày " + cut_year(startdate,simple=True) +"\n"
                    
                    
                    message += f"<b>Vietnam Airlines 12kg xách tay, 46kg ký gửi, giá vé = {to_price(giachot)}</b>"

                    
                        
                        
                    el = driver.find_element(By.XPATH, '//*[@id="fareShow"]/li[1]/div/div/div[3]/div')

                    # Scroll tới element cho chắc ăn
                    driver.execute_script("arguments[0].scrollIntoView(true);", el)
                    time.sleep(2)  # đợi nó render ngon lành

                    # Chụp full page trước
                    driver.save_screenshot("2ChieuVNANoituyen.png")

                    # Lấy vị trí & kích thước element
                    
                    send_telegram(message, bot_token=bot_token, chat_id=chat_id, driver=driver,img_path="2ChieuVNANoituyen.png")
                    print(message)
                    break
                    
                except Exception as e:
                    print("❌ Lỗi khi click:", e)
            else:
                print("❌ Hết chuyến bay nối tuyến")
            # 4. CLICK NẾU CHƯA CHỌN
            

            
        except Exception as e:
                print(f" {e}")

def check(data, spreadsheet_id):
    """
    Hàm xử lý dữ liệu từ Google Sheet
    :param data: Dữ liệu đọc được từ sheet
    :param spreadsheet_id: ID của spreadsheet
    """
    global bot_token
    global chat_id
    if data and len(data) > 0:
        # Tạo nội dung tin nhắn
        
        
        # Gọi các hàm xử lý dữ liệu
        if data[0][5] == "TRUE":
            print("check 2 chiều")
            checkVNA2chieu(data, spreadsheet_id)
        else:
            print("check 1 chiều")
            checkVNA1chieu(data, spreadsheet_id)
        
    else:
        print("Không có dữ liệu để xử lý")
def main():
    # ID của spreadsheet
    spreadsheet_id = CONFIG['SPREADSHEET_ID']
    
    print("Bắt đầu kiểm tra dữ liệu từ Google Sheet...")
    print("Nhấn Ctrl+C để dừng chương trình")
    
    try:
        # Khởi tạo ChromeDriver
        global driver
        
        while True:
            driver = setup_chrome_driver()
            # Đọc dữ liệu từ A2:E2
            data = read_sheet(spreadsheet_id, 'Hàng Chờ VNA!A2:I2')
            if data:
                print("\nCó hàng chờ cần check VNA")
                for row in data:
                    print(row)
                # Gọi hàm check() để xử lý dữ liệu
                try:
                    if data[0][5] and data[0][0] and data[0][1]:
                        check(data, spreadsheet_id)
                    # Xoá các ô A2, B2, F2 trong Google Sheet
                    delete_row_by_range(spreadsheet_id, 'Hàng Chờ VNA!A2:Z2')
                except:
                    send_telegram("Lỗi bot VNA, reconect", bot_token=bot_token, chat_id=chat_id)
            close_chrome_driver()
            # Đợi 5 giây trước khi kiểm tra lại
            time.sleep(4)
            
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình")
        close_chrome_driver()
   

if __name__ == "__main__":
    main() 