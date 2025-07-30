from telethon.sync import TelegramClient, events
import csv
import os
from datetime import datetime
import requests

# معلومات الحساب
api_id = 27477919
api_hash = "b25cce1727f6d33d41d9e00e3ed62583"
session_name = "session"

# معلومات الجروب المصدر
source_group = -1002717770463

# توكن البوت لإرسال الرسائل للمستخدم
bot_token = "7625110082:AAEvVtXtroNyX98_le7BnpnEuCxJ8wDXNk8"

# مسار مجلد الأرقام
DATA_FOLDER = "data"

# تحميل المستخدمين وأرقامهم من ملفات CSV
def load_users():
    users = {}
    for file in os.listdir(DATA_FOLDER):
        if file.endswith(".csv"):
            country = file.replace(".csv", "")
            with open(os.path.join(DATA_FOLDER, file), "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        user_id, number = row
                        users[number] = (int(user_id), country)
    return users

# استخراج الكود من النص (مثلاً 4-8 أرقام متتالية)
def extract_code(text):
    import re
    match = re.search(r"\b\d{4,8}\b", text)
    return match.group(0) if match else None

# إنشاء الجلسة
client = TelegramClient(session_name, api_id, api_hash)

# مراقبة الجروب الصديق
@client.on(events.NewMessage(chats=source_group))
async def handler(event):
    text = event.raw_text
    users = load_users()

    for number, (user_id, country) in users.items():
        if number in text:
            code = extract_code(text)
            if code:
                time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg = f"""
                تـــم اســـتلم كــــود جـــديــد
                لـرقـم: {number}
⏰الــوقــت : {time}
الــدولة 🌝: {country}
🔐الـــكـود: `{code}`
📝 الرسالة: {text}"""

                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    data={
                        "chat_id": user_id,
                        "text": msg,
                        "parse_mode": "Markdown"
                    }
                )
                break

# بدء الاتصال
client.start()
client.run_until_disconnected()