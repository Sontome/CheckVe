from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re

# Đường dẫn đến file credentials JSON
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'sontome-de382811160d.json'  # File credentials của bạn

# Telegram configuration
TELEGRAM_BOT_TOKEN = '5737041469:AAG5XdXVwATvldvDpXmnlQT0dmh2-sZ70gE'
TELEGRAM_CHAT_ID = str(-4622194613) # Đã sửa thành số nguyên
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

# Biến toàn cục để lưu driver
driver = None

def setup_chrome_driver():
    """
    Thiết lập và khởi động ChromeDriver
    :return: Đối tượng WebDriver
    """
    try:
        # Thiết lập options cho Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Chạy ẩn (bỏ comment nếu muốn chạy ẩn)
        
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

def send_telegram_message(message, image_path=None):
    """
    Gửi tin nhắn lên Telegram
    :param message: Nội dung tin nhắn
    :param image_path: Đường dẫn đến file ảnh (nếu có)
    :return: True nếu thành công, False nếu thất bại
    """
    try:
        if image_path:
            # Gửi ảnh kèm theo tin nhắn
            with open(image_path, 'rb') as photo:
                files = {'photo': photo}
                payload = {
                    'chat_id': TELEGRAM_CHAT_ID,
                    'caption': message,
                    'parse_mode': 'HTML'
                }
                response = requests.post(
                    f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto',
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
    print("Đang xử lý dữ liệu VJ...")
    loaive="ECO"
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
        username = 'KR242012A18KXM'
        password = 'Grgnbd@34562312'
        print(f"Đang nhập username: {username}")
        
        # Đợi cho element input username xuất hiện
        wait = WebDriverWait(driver, 10)
        username_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
        
        # Xóa nội dung hiện tại và nhập username mới
        username_input.clear()
        username_input.send_keys(username)
        
        password_input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        
        # Xóa nội dung hiện tại và nhập username mới
        password_input.clear()
        password_input.send_keys(password)
        username_input.send_keys(Keys.RETURN)  # Thêm phím Enter
        print(f"Đã nhập username: {username} và nhấn Enter")
        # Xử lý dữ liệu từ sheet
        for row in data:
            
            span_elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.mat-select-placeholder"))
            )
            
            # Click vào element span
            span_elements[0].click()
            print("Đã click vào element span")
            
            # Đợi một chút để dropdown hiển thị
            time.sleep(1)
            
            # Tìm element input tìm kiếm theo placeholder
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Tìm kiếm...']"))
            )
            
            # Xóa nội dung hiện tại và nhập nội dung từ row[0]
            search_input.clear()
            search_input.send_keys(row[0])
            print(f"Đã nhập nội dung tìm kiếm: {row[0]}")
            span_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.mat-select-placeholder"))
            )
            
            # Click vào element span
            span_element.click()
            print("Đã click vào element span")
            
            # Đợi một chút để dropdown hiển thị
            time.sleep(1)
            
            # Tìm element input tìm kiếm theo placeholder
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Tìm kiếm...']"))
            )
            
            # Xóa nội dung hiện tại và nhập nội dung từ row[0]
            search_input.clear()
            search_input.send_keys(row[1])
            print(f"Đã nhập nội dung tìm kiếm: {row[1]}")
            
            # Đợi một chút để kết quả tìm kiếm hiển thị
            
            
            # Tìm và click vào option chứa nội dung từ row[0]
            
            
            # Tìm element input ngày tháng năm
            try:
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

            

            span_elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.mat-button-wrapper"))
            )
            
            # Click vào element span
            span_elements[0].click()
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
            else :
                loaive="DELUXE"
                date_element_deluxe.click()
            # Đợi bảng thông tin chuyến bay xuất hiện
            # Đợi 5 giây để bảng hiển thị đầy đủ
            
            try:
                # Chụp ảnh toàn bộ trình duyệt
                time_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div[1]/div[3]/div[1]/div/div/div[1]/div[1]/app-list-flight/div[4]/div/div/div[2]/div/div[1]/div[1]/div[3]"))
                )
                # Lấy nội dung text của element
                time_text = time_element.text
                
                # Thay đổi định dạng thời gian
                time_text = time_text.replace(", ", " ngày ")
                price_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.font_22.color_white.font_money"))
                )
                time.sleep(0.5)
                # Lấy nội dung text của element
                price_text = price_element.text
                driver.save_screenshot("browser_screenshot.png")
                print("Đã chụp ảnh toàn bộ trình duyệt")
                
                # Gửi ảnh lên Telegram
                message = f"🔍 <b>Chiều Đi --></b>\n\n"
                message += f" {row[0]} - {row[1]} "
                message += f" {time_text} {loaive} "
                message += f" {str(price_text)}\n"
                
                
                if send_telegram_message(message, "browser_screenshot.png"):
                    print("Đã gửi ảnh toàn bộ trình duyệt lên Telegram")
                else:
                    print("Không thể gửi ảnh toàn bộ trình duyệt lên Telegram")
                
                # Lấy thông tin chuyến bay
                if row[5]=="TRUE":
                    checkVJback(data,time_text, price_text,loaive)
                else :
                    SPREADSHEET_ID = '1RyL5_rm7wFyR6VPpOl2WrsgFjbz2m1cNtATXR7DK190'
                    clear_range = 'CheckVe!L1:Q2'
                    clear_values = [[row[0], row[1],time_text, str(price_text),loaive,row[6 ]],['', '','', '','','']]  # Tạo danh sách rỗng cho 2 ô
                    update_sheet(SPREADSHEET_ID, clear_range, clear_values)
                    time.sleep(1)
                    datatele = read_sheet(SPREADSHEET_ID, 'CheckVe!A3:A6')
                    messtele = datatele[0][0] +"\n" +datatele[1][0] +"\n" + datatele[2][0] +"\n" +datatele[3][0] 
                    send_telegram_message(messtele)
                
            except Exception as e:
                print(f"Lỗi khi chụp bảng thông tin chuyến bay: {str(e)}")
                
    except Exception as e:
        print(f"Lỗi khi xử lý dữ liệu VJ: {str(e)}")
def checkVJback(data,time_text_0,price_text_0,loaive):
    """
    Hàm xử lý dữ liệu VJ từ Google Sheet
    :param data: Dữ liệu đọc được từ sheet
    """
    global driver
    print("Đang xử lý dữ liệu VJ...")
    loaiveve="ECO"
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
        wait = WebDriverWait(driver, 10)
        
        # Xử lý dữ liệu từ sheet
        for row in data:
            time.sleep(2)
            span_elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.mat-select-placeholder"))
            )
            
            # Click vào element span
            span_elements[0].click()
            print("Đã click vào element span")
            
            # Đợi một chút để dropdown hiển thị
            time.sleep(1)
            
            # Tìm element input tìm kiếm theo placeholder
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Tìm kiếm...']"))
            )
            
            # Xóa nội dung hiện tại và nhập nội dung từ row[0]
            search_input.clear()
            search_input.send_keys(row[1])
            print(f"Đã nhập nội dung tìm kiếm: {row[1]}")
            span_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.mat-select-placeholder"))
            )
            
            # Click vào element span
            span_element.click()
            print("Đã click vào element span")
            
            # Đợi một chút để dropdown hiển thị
            time.sleep(1)
            
            # Tìm element input tìm kiếm theo placeholder
            search_input = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Tìm kiếm...']"))
            )
            
            # Xóa nội dung hiện tại và nhập nội dung từ row[0]
            search_input.clear()
            search_input.send_keys(row[0])
            print(f"Đã nhập nội dung tìm kiếm: {row[0]}")
            
            # Đợi một chút để kết quả tìm kiếm hiển thị
            
            
            # Tìm và click vào option chứa nội dung từ row[0]
            
            
            # Tìm element input ngày tháng năm
            try:
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

            

            span_elements = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.mat-button-wrapper"))
            )
            
            # Click vào element span
            span_elements[0].click()
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
            else :
                loaiveve="DELUXE"
                date_element_deluxe.click()
            
            # Đợi bảng thông tin chuyến bay xuất hiện
            # Đợi 5 giây để bảng hiển thị đầy đủ
            
            try:
                # Chụp ảnh toàn bộ trình duyệt
                time_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-main-layout/div/div/app-booking-layout/div/div[1]/div[3]/div[1]/div/div/div[1]/div[1]/app-list-flight/div[4]/div/div/div[2]/div/div[1]/div[1]/div[3]"))
                )
                # Lấy nội dung text của element
                time_text = time_element.text
                
                # Thay đổi định dạng thời gian
                time_text = time_text.replace(", ", " ngày ")
                price_element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.font_22.color_white.font_money"))
                )
                time.sleep(0.5)
                # Lấy nội dung text của element
                price_text = price_element.text
                driver.save_screenshot("browser_screenshot.png")
                print("Đã chụp ảnh toàn bộ trình duyệt")
                
                # Gửi ảnh lên Telegram
                message = f"🔍 <b>Chiều Về</b> &lt;--\n\n"
                message += f" {row[1]} - {row[0]} "
                message += f" {time_text} {loaiveve}:"
                message += f" {str(price_text)}\n\n"
                SPREADSHEET_ID = '1RyL5_rm7wFyR6VPpOl2WrsgFjbz2m1cNtATXR7DK190'
                clear_range = 'CheckVe!L1:Q2'
                clear_values = [[row[0], row[1],time_text_0, str(price_text_0),loaive,row[6]],[row[1], row[0],time_text, str(price_text),loaiveve,'']]  # Tạo danh sách rỗng cho 2 ô
                update_sheet(SPREADSHEET_ID, clear_range, clear_values)
                
                if send_telegram_message(message, "browser_screenshot.png"):
                    print("Đã gửi ảnh toàn bộ trình duyệt lên Telegram")
                else:
                    print("Không thể gửi ảnh toàn bộ trình duyệt lên Telegram")
                datatele = read_sheet(SPREADSHEET_ID, 'CheckVe!A3:A6')
                messtele = datatele[0][0] +"\n" + datatele[1][0] +"\n" +datatele[2][0] +"\n" +datatele[3][0] 
                send_telegram_message(messtele)
                # Lấy thông tin chuyến bay
                
                
            except Exception as e:
                print(f"Lỗi khi chụp bảng thông tin chuyến bay: {str(e)}")
                
    except Exception as e:
        print(f"Lỗi khi xử lý dữ liệu VJ: {str(e)}")

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
    if data and len(data) > 0:
        # Tạo nội dung tin nhắn
        message = "🔔 <b>Loading...</b>\n\n"
        
        message +=  data[0][0] + " --> " +data[0][1] + " |  " 
        if data[0][5]== "TRUE":
            
            message += "Khứ Hồi"
        else :
            message += "1 Chiều"
        # Gửi tin nhắn lên Telegram
        if send_telegram_message(message):
            print("Đã gửi thông báo lên Telegram")
        else:
            print("Không thể gửi thông báo lên Telegram")
            
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
    SPREADSHEET_ID = '1RyL5_rm7wFyR6VPpOl2WrsgFjbz2m1cNtATXR7DK190'
    
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
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình")
        close_chrome_driver()
   

if __name__ == "__main__":
    main() 