import customtkinter as ctk
from tkinter import messagebox
import json
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

DEFAULT_USER = "1"
DEFAULT_PASS = "1"
CONFIG_FILE = "config.json"

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"vietjet": {}, "vna": {}}

class SetupWindow(ctk.CTkToplevel):
    def __init__(self, parent, airline):
        super().__init__(parent)
        self.title(f"Cài đặt {airline}")
        self.geometry("400x300")
        self.airline = airline
        self.config_data = load_config()

        ctk.CTkLabel(self, text="User", font=("Segoe UI", 14)).pack(pady=(20, 5))
        self.user_entry = ctk.CTkEntry(self, width=300)
        self.user_entry.pack()

        ctk.CTkLabel(self, text="Password", font=("Segoe UI", 14)).pack(pady=(15, 5))
        self.pass_entry = ctk.CTkEntry(self, width=300, show="*")
        self.pass_entry.pack()

        ctk.CTkLabel(self, text="Website", font=("Segoe UI", 14)).pack(pady=(15, 5))
        self.link_entry = ctk.CTkEntry(self, width=300)
        self.link_entry.pack()

        ctk.CTkButton(self, text="Lưu", command=self.save).pack(pady=20)

        self.load_existing_data()

    def load_existing_data(self):
        info = self.config_data.get(self.airline.lower(), {})
        self.user_entry.insert(0, info.get("user", ""))
        self.pass_entry.insert(0, info.get("pass", ""))
        self.link_entry.insert(0, info.get("link", ""))

    def save(self):
        self.config_data[self.airline.lower()] = {
            "user": self.user_entry.get(),
            "pass": self.pass_entry.get(),
            "link": self.link_entry.get()
        }
        save_config(self.config_data)
        messagebox.showinfo("Xong rồi", f"Đã lưu cài đặt cho {self.airline}")
        self.destroy()

class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Đăng nhập")
        self.geometry("600x300")
        self.resizable(False, False)

        ctk.CTkLabel(self, text="User", font=("Segoe UI", 14)).pack(pady=(40, 10))
        self.user_entry = ctk.CTkEntry(self, width=300)
        self.user_entry.pack()

        ctk.CTkLabel(self, text="Password", font=("Segoe UI", 14)).pack(pady=(20, 10))
        self.pass_entry = ctk.CTkEntry(self, show="*", width=300)
        self.pass_entry.pack()

        ctk.CTkButton(self, text="Đăng nhập", command=self.check_login, width=200, height=40, font=("Segoe UI", 14, "bold")).pack(pady=30)

        self.user_entry.insert(0, DEFAULT_USER)
        self.pass_entry.insert(0, DEFAULT_PASS)

    def check_login(self):
        if self.user_entry.get() == DEFAULT_USER and self.pass_entry.get() == DEFAULT_PASS:
            self.destroy()
            MainApp()
        else:
            messagebox.showerror("Sai rồi", "Đăng nhập xàm lol")

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🛫 App Check Vé Máy Bay")
        self.geometry("1000x600")
        self.minsize(800, 500)

        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(top_frame, text="Cài đặt VietJet", command=self.setup_vietjet).pack(side="left", padx=10)
        ctk.CTkButton(top_frame, text="Cài đặt VNA", command=self.setup_vna).pack(side="left", padx=10)
        ctk.CTkButton(top_frame, text="Bắt đầu", command=self.start_check).pack(side="right", padx=10)
        ctk.CTkButton(top_frame, text="Dừng", command=self.stop_check).pack(side="right")

        # === Thanh chọn thông tin tìm kiếm ===
        form_frame = ctk.CTkFrame(self)
        form_frame.pack(fill="x", padx=20, pady=(5, 0))

        self.from_combo = ctk.CTkComboBox(form_frame, values=["SGN", "HAN", "DAD"], width=100)
        self.from_combo.set("SGN")
        self.from_combo.pack(side="left", padx=5)

        self.to_combo = ctk.CTkComboBox(form_frame, values=["HAN", "SGN", "DAD"], width=100)
        self.to_combo.set("HAN")
        self.to_combo.pack(side="left", padx=5)

        self.depart_date = ctk.CTkEntry(form_frame, placeholder_text="Ngày đi (dd-mm-yyyy)", width=130)
        self.depart_date.pack(side="left", padx=5)

        self.return_date = ctk.CTkEntry(form_frame, placeholder_text="Ngày về (dd-mm-yyyy)", width=130)
        self.return_date.pack(side="left", padx=5)

        self.passenger_count = ctk.CTkComboBox(form_frame, values=[str(i) for i in range(1, 10)], width=80)
        self.passenger_count.set("1")
        self.passenger_count.pack(side="left", padx=5)

        ctk.CTkButton(form_frame, text="Check", command=self.send_form).pack(side="left", padx=10)

        # === Khung log chính ===
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(expand=True, fill="both", padx=20, pady=10)

        self.left_log = ctk.CTkTextbox(main_frame)
        self.left_log.pack(side="left", expand=True, fill="both", padx=10, pady=10)
        self.left_log.insert("end", "[VietJet Log]")

        self.right_log = ctk.CTkTextbox(main_frame)
        self.right_log.pack(side="right", expand=True, fill="both", padx=10, pady=10)
        self.right_log.insert("end", "[VNA Log]")

        # === Progress bar ===
        self.vietjet_progress = ctk.CTkProgressBar(self)
        self.vna_progress = ctk.CTkProgressBar(self)
        self.vietjet_progress.pack(fill="x", padx=25, pady=(0, 5))
        self.vna_progress.pack(fill="x", padx=25, pady=(0, 20))
        self.vietjet_progress.set(0)
        self.vna_progress.set(0)

        self.mainloop()

    def setup_vietjet(self):
        SetupWindow(self, "VietJet")

    def setup_vna(self):
        SetupWindow(self, "VNA")

    def start_check(self):
        self.left_log.insert("end", "\n👉 Bắt đầu kiểm tra VietJet...")
        self.right_log.insert("end", "\n👉 Bắt đầu kiểm tra VNA...")
        self.vietjet_progress.set(0.3)
        self.vna_progress.set(0.5)

    def stop_check(self):
        self.left_log.insert("end", "\n⛔ Đã dừng VietJet")
        self.right_log.insert("end", "\n⛔ Đã dừng VNA")
        self.vietjet_progress.set(0)
        self.vna_progress.set(0)

    def send_form(self):
        from_loc = self.from_combo.get()
        to_loc = self.to_combo.get()
        depart = self.depart_date.get()
        ret = self.return_date.get()
        pax = self.passenger_count.get()

        self.left_log.insert("end", f"\n📤 Đã gửi yêu cầu: {from_loc} -> {to_loc}, đi: {depart}, về: {ret}, {pax} người")
        self.left_log.see("end")

if __name__ == "__main__":
    LoginWindow().mainloop()
