import time
import requests
from io import BytesIO
from datetime import datetime
CONFIGTEST = {
    'SCOPES': ['https://www.googleapis.com/auth/spreadsheets'],
    'SERVICE_ACCOUNT_FILE': 'keytest.json',  # File credentials của bạn
    'SPREADSHEET_ID': '1OwKfz3bhJKai2ph6Fc8GOeN087hBU1jPY9dm02ZisQo',
    'TELEGRAM_BOT_TOKEN': '5737041469:AAG5XdXVwATvldvDpXmnlQT0dmh2-sZ70gE',
    'TELEGRAM_CHAT_ID': str(-4698930772),  # room tele chính
    
}
CONFIG=CONFIGTEST
TELEGRAM_API_URL = f'https://api.telegram.org/bot{CONFIG["TELEGRAM_BOT_TOKEN"]}/sendMessage'
bot_token = CONFIG['TELEGRAM_BOT_TOKEN']
chat_id = CONFIG['TELEGRAM_CHAT_ID']
def send_telegram(bot_token, chat_id, message, driver=None):
    """
    Gửi tin nhắn Telegram. Nếu truyền driver thì sẽ chụp screenshot trình duyệt và gửi kèm.
    """
    data = {
        'chat_id': chat_id,
        'parse_mode': 'HTML',
    }

    # Nếu có driver thì chụp ảnh và gửi kèm
    if driver is not None:
        screenshot = BytesIO()
        driver.save_screenshot(screenshot)
        screenshot.seek(0)

        files = {
            'photo': ('screenshot.png', screenshot)
        }
        data['caption'] = message

        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendPhoto",
            data=data,
            files=files
        )
    else:
        # Chỉ gửi text
        data['text'] = message
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=data
        )

    return response.status_code == 200

#send_telegram(bot_token,chat_id,'test')
chuoi_goc= 1245444
def cut_year(date_str: str) -> str:
    """
    Nhận chuỗi kiểu 'HH:MM ngày DD/MM/YYYY', trả về 'HH:MM ngày DD/MM'
    """
    try:
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
print(to_price(chuoi_goc))