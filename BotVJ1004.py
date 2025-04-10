from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import time
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

import re



CONFIG = {
    'SCOPES': ['https://www.googleapis.com/auth/spreadsheets'],
    'SERVICE_ACCOUNT_FILE': 'keytest.json',  # File credentials của bạn
    'SPREADSHEET_ID': '1RyL5_rm7wFyR6VPpOl2WrsgFjbz2m1cNtATXR7DK190',
    'TELEGRAM_BOT_TOKEN': '7359295123:AAGz0rHge3L5gM-XJmyzNq6sayULdHO4-qE',
    'TELEGRAM_CHAT_ID': str(-4622194613),  # room tele chính
    'usernameVJ' : 'KR242012A18KXM',
    'passwordVJ' : 'Grgnbd@34562312'
}
#test id
CONFIGTEST = {
    'SCOPES': ['https://www.googleapis.com/auth/spreadsheets'],
    'SERVICE_ACCOUNT_FILE': 'keytest.json',  # File credentials của bạn
    'SPREADSHEET_ID': '1OwKfz3bhJKai2ph6Fc8GOeN087hBU1jPY9dm02ZisQo',
    'TELEGRAM_BOT_TOKEN': '7359295123:AAGz0rHge3L5gM-XJmyzNq6sayULdHO4-qE',
    'TELEGRAM_CHAT_ID': str(-4698930772),  # room test
    'usernameVJ' : 'KR242009A18KXM',
    'passwordVJ' : 'Glvav@31613017'
    
}
CONFIG=CONFIGTEST


TELEGRAM_BOT_TOKEN= CONFIG['TELEGRAM_BOT_TOKEN']
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'



# Biến toàn cục để lưu driver
driver = None
username = CONFIG["usernameVJ"]
password = CONFIG["passwordVJ"]
def setup_chrome_driver():
    """
    Thiết lập và khởi động ChromeDriver
    :return: Đối tượng WebDriver
    """
    try:
        # Thiết lập options cho Chrome
        chrome_options = Options()
        #chrome_options.add_argument("--headless")  # Chạy ẩn (bỏ comment nếu muốn chạy ẩn)
        
        chrome_options.add_argument("--window-size=1920,1080")
        
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
def cut_year(date_str: str, simple: bool = False) -> str:
    """
    Cắt phần năm khỏi chuỗi ngày:
    - simple=False: 'HH:MM ngày DD/MM/YYYY' → 'HH:MM ngày DD/MM'
    - simple=True:
        + 'YYYY/MM/DD' → 'DD/MM'
        + 'MM/DD/YYYY' → 'DD/MM' (kiểu Mỹ)
    """
    try:
        if simple:
            try:
                # Format ISO: YYYY/MM/DD
                dt = datetime.strptime(date_str, "%Y/%m/%d")
                return dt.strftime("%d/%m")
            except ValueError:
                # Format US: MM/DD/YYYY
                dt = datetime.strptime(date_str, "%m/%d/%Y")
                return dt.strftime("%d/%m")
        else:
            # Format đầy đủ: HH:MM ngày DD/MM/YYYY
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
def giacuoi(*loai_ve):
    """
    Tính phụ phí cuối cùng dựa theo loại vé:
    - Vé 2 chiều ECO + ECO         → +110000
    - Vé 2 chiều ECO + DELUXE      → +70000
    - Vé 1 chiều DELUXE            → +35000
    - Vé 1 chiều ECO               → +72000
    """
    loai_ve = [ve.upper() for ve in loai_ve]  # chuẩn hóa chữ hoa
    if len(loai_ve) == 2:
        if set(loai_ve) == {"ECO"}:
            return 110_000
        elif "ECO" in loai_ve and "DELUXE" in loai_ve:
            return 70_000
        else:
            print("❌ Loại vé 2 chiều không hợp lệ:", loai_ve)
            return 0
    elif len(loai_ve) == 1:
        if loai_ve[0] == "ECO":
            return 72_000
        elif loai_ve[0] == "DELUXE":
            return 35_000
        else:
            print("❌ Loại vé 1 chiều không hợp lệ:", loai_ve[0])
            return 0
    else:
        print("❌ Số lượng vé không hợp lệ:", loai_ve)
        return 0
def to_price(amount: int, currency: str = "KRW", round_to: int = 100) -> str:
    """
    Chuyển số nguyên thành chuỗi kiểu '1,138,300 KRW'
    Làm tròn đến gần nhất round_to (mặc định 100)
    """
    try:
        # Làm tròn đến gần nhất 'round_to'
        rounded = round(amount / round_to) * round_to
        formatted = f"{rounded:,}"
        return f"{formatted} {currency}"
    except:
        print(f"❌ Không convert được: {amount}")
        return str(amount)
def send_telegram_message(message, image_paths=None):
    """
    Gửi tin nhắn lên Telegram
    :param message: Nội dung tin nhắn
    :param image_paths: List đường dẫn đến các file ảnh (nếu có)
    :return: True nếu thành công, False nếu thất bại
    """
    TELEGRAM_CHAT_ID = CONFIG['TELEGRAM_CHAT_ID']
    try:
        if image_paths and len(image_paths) > 0:
            media = []
            files = {}

            for idx, image_path in enumerate(image_paths):
                file_key = f'photo{idx}'
                files[file_key] = open(image_path, 'rb')
                media.append({
                    'type': 'photo',
                    'media': f'attach://{file_key}',
                    'caption': message if idx == 0 else "",  # ⚠️ fix lỗi ở đây
                    'parse_mode': 'HTML'
                })

            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'media': json.dumps(media)
            }

            response = requests.post(
                f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMediaGroup',
                data=payload,
                files=files
            )
        else:
            # Chỉ gửi tin nhắn
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(TELEGRAM_API_URL, json=payload)

        if response.status_code == 200:
            return True
        else:
            print(f"Lỗi khi gửi tin nhắn Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"Lỗi khi gửi tin nhắn Telegram: {str(e)}")
        return False

def get_google_sheets_service():
    try:
        SCOPES = CONFIG['SCOPES']
        SERVICE_ACCOUNT_FILE = CONFIG['SERVICE_ACCOUNT_FILE']
        # Đọc credentials từ file JSON
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
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
def checkVJ(data):
    """
    Hàm xử lý dữ liệu VJ từ Google Sheet
    :param data: Dữ liệu đọc được từ sheet
    """
    global driver
    global username
    global password
    print("Đang xử lý dữ liệu VJ...")
    loaive=" ⛔ Hết Vé "
    # Kiểm tra nếu driver chưa được khởi tạo
    if not driver:
        driver = setup_chrome_driver()
        if not driver:
            print("Không thể khởi động ChromeDriver cho VJ")
            return
    
    # TODO: Thêm logic xử lý dữ liệu VJ ở đây
    # Ví dụ: Mở trang web và xử lý dữ liệu
    try:
        # Mở trang web (thay thế URL bằng trang web thực tế)
        driver.get("https://agents2.vietjetair.com/login")
        print("Đã mở trang web cho VJ")
        
        print(f"Đang nhập username: {username}")
        
        # Đợi cho element input username xuất hiện
        wait = WebDriverWait(driver, 30)
        for field_name, value in [("username", username), ("password", password)]:
            input_elem = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"input[name='{field_name}']")))
            input_elem.clear()
            input_elem.send_keys(value)

        # Enter sau khi nhập xong password
        input_elem.send_keys(Keys.RETURN)
        print(f"✅ Đã nhập username: {username} và nhấn Enter")
        # Xử lý dữ liệu từ sheet
        for row in data:
            
            # Chờ tới khi dropdown render ra
            options = [row[0], row[1]]

            # Tìm 2 cái dropdown
            dropdown_xpaths = [
                
                "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div/div[3]/div[1]/div/div/div[1]/app-date-destination/div/section[1]/div/form/div[2]/mat-form-field[1]/div/div[1]/div/mat-select/div/div[1]",
                "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div/div[3]/div[1]/div/div/div[1]/app-date-destination/div/section[1]/div/form/div[3]/mat-form-field[1]/div/div[1]/div/mat-select/div/div[1]"
            ]
            print(f"✅  bắt đầu chọn option...")
            input_xpaths = [
                
                "/html/body/div[2]/div[2]/div/div/div/mat-option[1]/span/ngx-mat-select-search/div/input",
                "/html/body/div[2]/div[2]/div/div/div/mat-option[1]/span/ngx-mat-select-search/div/input"
            ]
            # Xử lý từng cái dropdown
            
            try:
                wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, "cdk-overlay-backdrop")) == 0)
                date_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[formcontrolname='departureDate']"))
                )
                
                # Đặt ngày tháng năm mong muốn (ví dụ: 2025-04-05)
                desired_date = str(row[3])  # Thay đổi ngày tháng năm theo ý muốn
                
                # Sử dụng JavaScript để đặt giá trị trực tiếp
                driver.execute_script(
                    "arguments[0].value = arguments[1]; "
                    "arguments[0].dispatchEvent(new Event('input', { bubbles: true })); "
                    "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                    date_input, desired_date
                )
                
                print(f"Đã đặt ngày tháng năm: {desired_date}")
                
                # Đợi một chút để đảm bảo giá trị đã được cập nhật
                
                
            except Exception as e:
                print(f"Lỗi khi đặt ngày tháng năm: {str(e)}")
            wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, "cdk-overlay-backdrop")) == 0)
            dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpaths[0]))).click()
            
            print(f"👉 Click dropdown thứ {1}")
            
            # Chờ ô input search hiện ra
            search_input = wait.until(
                EC.presence_of_element_located((By.XPATH, input_xpaths[0]))
            )
            search_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, input_xpaths[0]))
            )
            search_input.send_keys(options[0])
            print(f"⌨️ Gõ '{options[0]}'")
            wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, "cdk-overlay-backdrop")) == 0)
            dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpaths[1])))
            dropdown.click()

            print(f"👉 Click dropdown thứ {2}")
            
            # Chờ ô input search hiện ra
            search_input = wait.until(
                EC.visibility_of_element_located((By.XPATH, input_xpaths[1]))
            )
            search_input.send_keys(options[1])
            print(f"⌨️ Gõ '{options[1]}'")
                # Delay tí để nó render option
                
            
            # Tìm element input tìm kiếm theo placeholder
            
            
            # Đợi một chút để kết quả tìm kiếm hiển thị
            
            
            # Tìm và click vào option chứa nội dung từ row[0]
            
            
            # Tìm element input ngày tháng năm
            

            
            wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, "cdk-overlay-backdrop")) == 0)
            buttontimkiem= wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div/div[3]/div[1]/div/div/div[1]/app-date-destination/div/section[1]/div/form/div[6]/div[1]/button")))
            buttontimkiem.click()
            # Click vào element span
            try:
                date_element_eco = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div[1]/div[3]/div[1]/div/div/div[1]/div[1]/app-list-flight/div[4]/div/div/div/div[2]/div[4]/span/span[1]"))
                )

                date_element_deluxe = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div[1]/div[3]/div[1]/div/div/div[1]/div[1]/app-list-flight/div[4]/div/div/div/div[2]/div[3]/span/span[1]"))
                )
                ecovalue= date_element_eco.text.replace(",", "")
                deluxevalue= date_element_deluxe.text.replace(",", "")
                if int(ecovalue)<int(deluxevalue)-40000:
                    date_element_eco.click()
                    loaive="ECO"
                else :
                    loaive="DELUXE"
                    date_element_deluxe.click()
            # Đợi bảng thông tin chuyến bay xuất hiện
            # Đợi 5 giây để bảng hiển thị đầy đủ
            except Exception as e:
                driver.save_screenshot("browser_screenshot_start.png")
                print("không có vé nào ")
                
                # Gửi ảnh lên Telegram
                message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n"+row[0]+"-->"+row[1]+"\n\n ---<b>VietJet</b>--- " # icon VNA + in đậm tên khách
                if data[0][5] == "TRUE":
                    message += "🔁 Khứ Hồi\n\n"
                else:
                    message += "➡️ 1 Chiều\n\n"
                message += f" {row[0]} - {row[1]} "
                message += f" ngày {cut_year(desired_date,simple=True)} {loaive} \n"
                
                
                
                
              
                if row[5]=="TRUE":
                    
                    checkVJback(data,'Hết Vé', 'Hết Vé',loaive,message)
                    break
                else:
                    message +=f"<b>Giá Vé : đổi ngày check lại </b>"
                    if send_telegram_message(message, ["browser_screenshot_start.png"]):
                        print("Đã gửi ảnh toàn bộ trình duyệt lên Telegram")
                        break
            try:
                # Chụp ảnh toàn bộ trình duyệt
                wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, "cdk-overlay-backdrop")) == 0)
                time_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div[1]/div[3]/div[1]/div/div/div[1]/div[1]/app-list-flight/div[4]/div/div/div[2]/div/div[1]/div[1]/div[3]"))
                )
                time.sleep(3)
                # Lấy nội dung text của element
                time_text = time_element.text
                
                # Thay đổi định dạng thời gian
                time_text = time_text.replace(", ", " ngày ")
                
                
                
                price_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.font_22.color_white.font_money"))
                )
                # Lấy nội dung text của element
                price_text = price_element.text
                driver.save_screenshot("browser_screenshot_start.png")
                print("Đã chụp ảnh toàn bộ trình duyệt")
                
                # Gửi ảnh lên Telegram
                message = "👤Tên Khách: <b> " + data[0][6] + "</b>\n"+row[0]+"-->"+row[1]+"\n\n ---<b>VietJet</b>--- " # icon VNA + in đậm tên khách
                if data[0][5] == "TRUE":
                    message += "🔁 Khứ Hồi\n\n"
                else:
                    message += "➡️ 1 Chiều\n\n"
                message += f" {row[0]} - {row[1]} "
                message += f" ngày {cut_year(desired_date,simple=True)} {loaive} "
                message += f" {to_price(to_value(price_text))}\n"
                
                
                
                
                # Lấy thông tin chuyến bay
                if row[5]=="TRUE":
                   
                    checkVJback(data,time_text, price_text,loaive,message)
                    break
                else:
                    giacuoi = to_value(price_text)+giacuoi(loaive)
                    message += f"<b>\nGiá Vé {to_price((giacuoi))}</b>\n"
                    if send_telegram_message(message, ["browser_screenshot_start.png"]):
                        print("Đã gửi ảnh toàn bộ trình duyệt lên Telegram")
                    else:
                        print("Không thể gửi ảnh toàn bộ trình duyệt lên Telegram")
                
            except Exception as e:
                print('lỗi có vé ấn vào khong load được thông tin vé')
                send_telegram_message(message, ["browser_screenshot_start.png"])
                
                
    except Exception as e:
        print(f"Lỗi khi xử lý dữ liệu VJ: {str(e)}")
def checkVJback(data,time_text_0,price_text_0,loaive,message):
    """
    Hàm xử lý dữ liệu VJ từ Google Sheet
    :param data: Dữ liệu đọc được từ sheet
    """
    global driver
    print("Đang xử lý dữ liệu VJ...")
    loaiveve=" ⛔ Hết Vé "
    # Kiểm tra nếu driver chưa được khởi tạo
    if not driver:
        driver = setup_chrome_driver()
        if not driver:
            print("Không thể khởi động ChromeDriver cho VJ")
            return
    
    # TODO: Thêm logic xử lý dữ liệu VJ ở đây
    # Ví dụ: Mở trang web và xử lý dữ liệu
    try:
        # Mở trang web (thay thế URL bằng trang web thực tế)
        driver.get("https://agents2.vietjetair.com/login")
        print("Đã mở trang web cho VJback")
        
        
        # Đợi cho element input username xuất hiện
        wait = WebDriverWait(driver, 30)
        
        # Xử lý dữ liệu từ sheet
        for row in data:
            options = [row[1], row[0]]

            # Tìm 2 cái dropdown
            dropdown_xpaths = [
                
                "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div/div[3]/div[1]/div/div/div[1]/app-date-destination/div/section[1]/div/form/div[2]/mat-form-field[1]/div/div[1]/div/mat-select/div/div[1]",
                "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div/div[3]/div[1]/div/div/div[1]/app-date-destination/div/section[1]/div/form/div[3]/mat-form-field[1]/div/div[1]/div/mat-select/div/div[1]"
            ]
            print(f"✅  bắt đầu chọn option...")
            input_xpaths = [
                
                "/html/body/div[2]/div[2]/div/div/div/mat-option[1]/span/ngx-mat-select-search/div/input",
                "/html/body/div[2]/div[2]/div/div/div/mat-option[1]/span/ngx-mat-select-search/div/input"
            ]
            # Xử lý từng cái dropdown
            
            try:
                wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, "cdk-overlay-backdrop")) == 0)
                date_input = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[formcontrolname='departureDate']"))
                )
                
                # Đặt ngày tháng năm mong muốn (ví dụ: 2025-04-05)
                desired_date = str(row[4])  # Thay đổi ngày tháng năm theo ý muốn
                
                # Sử dụng JavaScript để đặt giá trị trực tiếp
                driver.execute_script(
                    "arguments[0].value = arguments[1]; "
                    "arguments[0].dispatchEvent(new Event('input', { bubbles: true })); "
                    "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
                    date_input, desired_date
                )
                
                print(f"Đã đặt ngày tháng năm: {desired_date}")
                
                # Đợi một chút để đảm bảo giá trị đã được cập nhật
                
                
            except Exception as e:
                print(f"Lỗi khi đặt ngày tháng năm: {str(e)}")
            wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, "cdk-overlay-backdrop")) == 0)
            dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpaths[0]))).click()
            
            print(f"👉 Click dropdown thứ {1}")
            
            # Chờ ô input search hiện ra
            search_input = wait.until(
                EC.presence_of_element_located((By.XPATH, input_xpaths[0]))
            )
            search_input = wait.until(
                EC.element_to_be_clickable((By.XPATH, input_xpaths[0]))
            )
            search_input.send_keys(options[0])
            print(f"⌨️ Gõ '{options[0]}'")
            wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, "cdk-overlay-backdrop")) == 0)
            dropdown = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpaths[1])))
            dropdown.click()

            print(f"👉 Click dropdown thứ {2}")
            
            # Chờ ô input search hiện ra
            search_input = wait.until(
                EC.visibility_of_element_located((By.XPATH, input_xpaths[1]))
            )
            search_input.send_keys(options[1])
            print(f"⌨️ Gõ '{options[1]}'")
                # Delay tí để nó render option
                
            
            # Tìm element input tìm kiếm theo placeholder
            
            
            # Đợi một chút để kết quả tìm kiếm hiển thị
            
            
            # Tìm và click vào option chứa nội dung từ row[0]
            
            
            # Tìm element input ngày tháng năm
            

            
            wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, "cdk-overlay-backdrop")) == 0)
            buttontimkiem= wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div/div[3]/div[1]/div/div/div[1]/app-date-destination/div/section[1]/div/form/div[6]/div[1]/button")))
            buttontimkiem.click()
            # Click vào element span
            try:
                date_element_eco = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div[1]/div[3]/div[1]/div/div/div[1]/div[1]/app-list-flight/div[4]/div/div/div/div[2]/div[4]/span/span[1]"))
                )

                date_element_deluxe = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div[1]/div[3]/div[1]/div/div/div[1]/div[1]/app-list-flight/div[4]/div/div/div/div[2]/div[3]/span/span[1]"))
                )
                ecovalue= date_element_eco.text.replace(",", "")
                deluxevalue= date_element_deluxe.text.replace(",", "")
                if int(ecovalue)<int(deluxevalue)-40000:
                    date_element_eco.click()
                    loaiveve="ECO"
                else :
                    loaiveve="DELUXE"
                    date_element_deluxe.click()
            except Exception as e:
                print('Không có vé chiều về')
                driver.save_screenshot("browser_screenshot_back.png")
                print("Đã chụp ảnh toàn bộ trình duyệt")
                
                # Gửi ảnh lên Telegram
                message += f" {row[0]} - {row[1]} "
                message += f" ngày {cut_year(desired_date,simple=True)} {loaive} "
                message += f" {to_price(to_value(price_text))}\n"
                
                
                
                if send_telegram_message(message, ["browser_screenshot_back.png"]):
                    print("Đã gửi ảnh toàn bộ trình duyệt lên Telegram")
                else:
                    print("Không thể gửi ảnh toàn bộ trình duyệt lên Telegram")
                
            # Đợi bảng thông tin chuyến bay xuất hiện
            # Đợi 5 giây để bảng hiển thị đầy đủ
            
            try:
                # Chụp ảnh toàn bộ trình duyệt
                wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, "cdk-overlay-backdrop")) == 0)
                time_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div[1]/div[3]/div[1]/div/div/div[1]/div[1]/app-list-flight/div[4]/div/div/div[2]/div/div[1]/div[1]/div[3]"))
                )
                time.sleep(3)
                # Lấy nội dung text của element
                time_text = time_element.text
                
                # Thay đổi định dạng thời gian
                
                
                
                
                price_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.font_22.color_white.font_money"))
                )
                # Lấy nội dung text của element
                price_text_ve = price_element.text
                driver.save_screenshot("browser_screenshot_back.png")
                print("Đã chụp ảnh toàn bộ trình duyệt")
                
                # Gửi ảnh lên Telegram
                
                message += f" {row[1]} - {row[0]} "
                message += f" ngày {cut_year(desired_date,simple=True)} {loaiveve}:"
                message += f" {to_price(to_value(price_text_ve))}\n\n"
                
                if (loaive == " ⛔ Hết Vé " or loaiveve ==" ⛔ Hết Vé "):
                    message += f"<b>Giá Vé : đổi ngày check lại </b>"
                else:
                    giacuoi = to_value(price_text_ve)+giacuoi(loaive,loaiveve)
                    message += f"<b>Giá Vé :"+ giacuoi   +" </b>"
                if send_telegram_message(message, ["browser_screenshot_start.png","browser_screenshot_back.png"]):
                    print("Đã gửi ảnh toàn bộ trình duyệt lên Telegram")
                else:
                    print("Không thể gửi ảnh toàn bộ trình duyệt lên Telegram")
                
                # Lấy thông tin chuyến bay
                
                
            except Exception as e:
                print('chưa biet')
                
    except Exception as e:
        print(f"Lỗi khi xử lý dữ liệu VJback: {str(e)}")

def checkVNA(data):
    """
    Hàm xử lý dữ liệu VNA từ Google Sheet
    :param data: Dữ liệu đọc được từ sheet
    """
    global driver
    print("Đang xử lý dữ liệu VNA...")
    
    # Kiểm tra nếu driver chưa được khởi tạo
    if not driver:
        driver = setup_chrome_driver()
        if not driver:
            print("Không thể khởi động ChromeDriver cho VNA")
            return
    
    # TODO: Thêm logic xử lý dữ liệu VNA ở đây
    # Ví dụ: Mở trang web và xử lý dữ liệu
    try:
        # Mở trang web (thay thế URL bằng trang web thực tế)
        driver.get("https://www.example.com")
        print("Đã mở trang web cho VNA")
        
        # Xử lý dữ liệu từ sheet
        for row in data:
            print("VNA Data:", row)
            # TODO: Thêm logic xử lý dữ liệu VNA cụ thể ở đây
            
    except Exception as e:
        print(f"Lỗi khi xử lý dữ liệu VNA: {str(e)}")

def check(data):
    """
    Hàm xử lý dữ liệu từ Google Sheet
    :param data: Dữ liệu đọc được từ sheet
    """
    global SPREADSHEET_ID
    if data and len(data) > 0:
        # Tạo nội dung tin nhắn
        
            
        # Gọi các hàm xử lý dữ liệu
        checkVJ(data)
        
        
        # checkVNA(data)

    else:
        print("Không có dữ liệu để xử lý")

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

def main():
    # ID của spreadsheet
    SPREADSHEET_ID = CONFIG['SPREADSHEET_ID']
    
    print("Bắt đầu kiểm tra dữ liệu từ Google Sheet...")
    print("Nhấn Ctrl+C để dừng chương trình")
    
    try:
        # Khởi tạo ChromeDriver
        global driver
        
        
        while True:
            driver = setup_chrome_driver()
            # Đọc dữ liệu từ A2:E2
            data = read_sheet(SPREADSHEET_ID, 'Hàng Chờ!A2:I2')
            if data:
                print("\nDữ liệu đọc được từ sheet CheckVe (A2:F2):")
                for row in data:
                    print(row)
                # Gọi hàm check() để xử lý dữ liệu
                if data[0][5] and data[0][0] and data[0][1]:
                    check(data)
                # Xoá các ô A2, B2, F2 trong Google Sheet
                    delete_row_by_range(SPREADSHEET_ID,'Hàng Chờ!A2:Z2')
                close_chrome_driver()
            else:
                print("\nKhông có dữ liệu hoặc có lỗi khi đọc dữ liệu")
                close_chrome_driver()
            # Đợi 5 giây trước khi kiểm tra lại
            time.sleep(4)
            
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình")
        close_chrome_driver()
   

if __name__ == "__main__":
    main() 