import undetected_chromedriver as uc
import time

if __name__ == '__main__':
    # --- Khởi tạo Options (Tùy chọn, giống như với Selenium thông thường) ---
    options = uc.ChromeOptions()

    # Bạn có thể thêm các tùy chọn ở đây nếu cần, ví dụ:
    # options.add_argument('--headless=new') # Chạy ở chế độ ẩn (headless mới, khó bị phát hiện hơn headless cũ)
    # options.add_argument('--user-agent=YOUR_REALISTIC_USER_AGENT_STRING') # Đặt User Agent tùy chỉnh
    # options.add_argument('--window-size=1920,1080') # Đặt kích thước cửa sổ

    # --- Khởi tạo driver ---
    # Sử dụng uc.Chrome thay vì webdriver.Chrome
    print("Đang khởi tạo Undetected ChromeDriver...")
    try:
        driver = uc.Chrome(options=options, version_main=135) # Thay 119 bằng phiên bản Chrome chính của bạn nếu cần
        print("Đã khởi tạo Driver thành công.")
    except Exception as e:
        print(f"Lỗi khi khởi tạo Driver: {e}")
        # Có thể bạn cần tải chromedriver tương ứng với phiên bản Chrome của mình
        # và đặt đường dẫn tới nó bằng tham số driver_executable_path
        # driver = uc.Chrome(options=options, driver_executable_path='/path/to/your/chromedriver')
        exit() # Thoát nếu không khởi tạo được driver


    # --- Mở trang web mục tiêu ---
    target_url = "https://cloudflare.com/vi-vn/products/turnstile/" # Thay bằng URL bạn muốn kiểm tra
    print(f"Đang truy cập: {target_url}")
    driver.get(target_url)

    # --- Chờ một chút để trang tải hoặc để quan sát ---
    print("Đã tải trang. Chờ 10 giây...")
    time.sleep(10)

    # --- (Tùy chọn) Thêm code của bạn để tương tác với trang web ở đây ---
    # Ví dụ: tìm phần tử, điền form, click nút,...
    # element = driver.find_element(By.ID, "some_id")
    # element.click()
    print("Thực hiện xong các thao tác (nếu có).")

    # --- Đóng trình duyệt ---
    print("Đang đóng trình duyệt...")
    driver.quit()
    print("Đã đóng trình duyệt.")