import asyncio
from playwright.async_api import async_playwright
import time
import json
import os

DATA_FILE = "chat_log.json"

def load_existing_logs():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_logs(logs):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(storage_state="telegram_login.json")
        page = await context.new_page()

        # Truy cập vào nhóm Telegram qua URL
        await page.goto("https://web.telegram.org/k/#-4622194613")
        selector = "a.chatlist-chat[href='#-4622194613']"

        # Click vào nhóm
        await page.click(selector)
        print("✅ Đã click vào nhóm Check vé live!")
        print("🔥 Vào nhóm thành công! Đang đọc chat...")

        await asyncio.sleep(5)

        # Load dữ liệu đã lưu
        logs = load_existing_logs()
        existing_messages = set(msg["content"] for msg in logs)

        while True:
            messages = await page.query_selector_all("div.message.spoilers-container.mt-shorter")

            print(f"📦 Tìm thấy {len(messages)} tin nhắn")

            new_count = 0

            for i, msg in enumerate(messages):
                try:
                    content = await msg.inner_text()
                    content = content.strip()

                    if content not in existing_messages:
                        logs.append({
                            "index": len(logs) + 1,
                            "content": content
                        })
                        existing_messages.add(content)
                        new_count += 1
                        print(f"[+] Thêm tin mới [{len(logs)}]: {content[:50]}...")
                except Exception as e:
                    print(f"❌ Lỗi đọc tin nhắn [{i+1}]: {e}")

            if new_count > 0:
                save_logs(logs)
                print(f"💾 Đã lưu {new_count} tin mới!")

            print("🕒 Đợi 30s rồi quét lại...")
            await asyncio.sleep(30)

asyncio.run(run())