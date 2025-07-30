import os
import telebot
from telebot import types
from telebot.types import BotCommand
import csv
import re
import json
API_TOKEN = '7625110082:AAEvVtXtroNyX98_le7BnpnEuCxJ8wDXNk8'  # ← غيّر هذا بتوكن البوت
ADMIN_ID = 8102220739  # ← غيّر هذا بمعرفك كأدمن
REQUIRED_CHANNEL = '@otp_albrans'
WARN_FILE = "warned_users.json"    # ملف لتخزين ID رسالة التحذير

bot = telebot.TeleBot(API_TOKEN)

BotCommand("start", "⚡ بدء البوت")
BotCommand("admin", "🛠️ خاص بي المدير")
BotCommand("Albrans", "🥹 ممنوع الضغط")
NUMBER_USER_FILE = "data/number_user.json"
DATA_FOLDER = 'data'
USERS_FILE = os.path.join(DATA_FOLDER, 'users.txt')
VERIFIED_FILE = os.path.join(DATA_FOLDER, "verified_users.json")
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
# ⬇️ أضف هنا دالة استخراج الكود OTP
def extract_otp(text):
    match = re.search(r"\b\d{4,8}\b", text)
    if match:
        return match.group(0)
    return None

# ⬇️ بعدها تأتي دوال أخرى مثل:
def save_user(user_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            f.write(str(user_id) + "\n")
    else:
        with open(USERS_FILE, "r") as f:
            users = f.read().splitlines()
        if str(user_id) not in users:
            with open(USERS_FILE, "a") as f:
                f.write(str(user_id) + "\n")

if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
# ✅ التحقق من الاشتراك في القناة
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False
# ✅ ملف التحقق من المشتركين مرة واحدة فقط
VERIFIED_FILE = os.path.join(DATA_FOLDER, "verified_users.json")

def has_been_verified(user_id):
    if not os.path.exists(VERIFIED_FILE):
        return False
    with open(VERIFIED_FILE, "r") as f:
        data = json.load(f)
    return str(user_id) in data

def mark_verified(user_id):
    if not os.path.exists(VERIFIED_FILE):
        data = {}
    else:
        with open(VERIFIED_FILE, "r") as f:
            data = json.load(f)
    data[str(user_id)] = True
    with open(VERIFIED_FILE, "w") as f:
        json.dump(data, f)
# ✅ رسالة /start
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or "غير معروف"
    username = "@" + message.from_user.username if message.from_user.username else "لا يوجد"

    # ✅ التحقق من الاشتراك في القناة
    if not is_subscribed(user_id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✅ اضغط هنا للاشتراك", url=f"https://t.me/{REQUIRED_CHANNEL.lstrip('@')}"))
        sent = bot.send_message(message.chat.id, "عذراً عزيزي، يجب عليك الاشتراك في القناة لاستخدام البوت ✅.", reply_markup=markup)

        # ✅ حفظ ID الرسالة للمستخدم (لحذفها لاحقاً)
        if os.path.exists(WARN_FILE):
            with open(WARN_FILE, "r") as f:
                data = json.load(f)
        else:
            data = {}

        data[str(user_id)] = sent.message_id

        with open(WARN_FILE, "w") as f:
            json.dump(data, f)

        return

    # ✅ حذف رسالة الاشتراك السابقة إن وجدت
    if os.path.exists(WARN_FILE):
        with open(WARN_FILE, "r") as f:
            data = json.load(f)
        if str(user_id) in data:
            try:
                bot.delete_message(user_id, data[str(user_id)])
            except:
                pass
            del data[str(user_id)]
            with open(WARN_FILE, "w") as f:
                json.dump(data, f)

    # ✅ التحقق من إرسال رسالة الاشتراك مرة واحدة فقط
    if not has_been_verified(user_id):
        bot.send_message(user_id, "✅ تم التحقق من الاشتراك بنجاح! اضغط /start")
        mark_verified(user_id)
        return

    # ✅ إرسال إشعار دخول جديد للأدمن
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            f.write("")
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()

    if str(user_id) not in users:
        total_users = len(users) + 1
        new_user_msg = f"""🟢 تم دخول شخص جديد
👤 الاسم: {first_name}
🔗 اليوزر: {username}
👥 عدد المستخدمين: {total_users}"""
        bot.send_message(ADMIN_ID, new_user_msg)

        with open(USERS_FILE, "a") as f:
            f.write(str(user_id) + "\n")

    # ✅ رسالة الترحيب واختيار الدولة
    welcome_text = (
        "💬 *مرحبا بك في بوت Albrans SMS*\n"
        "🎉 نحن هنا لنساعدك في استقبال رموز التفعيل (OTP) من مختلف الدول والخدمات بسهولة وسرعة!\n\n"
        "🌍 اختر الدولة التي ترغب بالحصول على رقم منها عبر الأزرار بالأسفل 👇"
    )

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".csv"):
            country = filename.replace(".csv", "")
            keyboard.add(types.InlineKeyboardButton(text=country, callback_data=f"country_{country}"))

    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=keyboard)
# ✅ اختيار الدولة وإرسال رقم
@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def assign_number(call):
    country = call.data.split("_", 1)[1]
    user_id = call.message.chat.id
    file_path = os.path.join(DATA_FOLDER, f"{country}.csv")

    if not os.path.exists(file_path):
        bot.send_message(user_id, "❌ لم يتم العثور على ملف الأرقام.")
        return

    with open(file_path, "r") as f:
        lines = f.readlines()

    if not lines:
        bot.send_message(user_id, "❌ لا توجد أرقام متاحة حالياً.")
        return

    number = lines.pop(0).strip()

    with open(file_path, "w") as f:
        f.writelines(lines)

    # 🟢 حفظ الرقم للمستخدم
    if not os.path.exists(NUMBER_USER_FILE):
        with open(NUMBER_USER_FILE, "w") as f:
            json.dump({}, f)

    with open(NUMBER_USER_FILE, "r") as f:
        data = json.load(f)

    data[number] = {
        "user_id": user_id,
        "country": country
    }

    with open(NUMBER_USER_FILE, "w") as f:
        json.dump(data, f)

    # رسالة الرقم + زر تغيير
    text = (
        "*تـم شـراء رقـم جـديـد لـك 🔰*\n\n"
        f"*الـرقـــــم :* `{number}`\n"
        f"*الـدولـة :* {country}\n"
        "*الـتـطـبـيـق :* whatsapp\n"
        "*الـحـالـة :* فـــي الإنـتـظـار ❗️."
    )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("تغيير الرقم 🔄", callback_data=f"change_{country}"))

    bot.edit_message_text(chat_id=user_id,
                          message_id=call.message.message_id,
                          text=text,
                          parse_mode="Markdown",
                          reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: call.data.startswith("country_"))
def handle_country(call):
    country = call.data.split("_", 1)[1]
    assign_number_core(chat_id=call.message.chat.id, message_id=call.message.message_id, country=country)
@bot.callback_query_handler(func=lambda call: call.data.startswith("change_"))
def handle_change_number(call):
    country = call.data.split("_", 1)[1]
    assign_number_core(chat_id=call.message.chat.id, message_id=call.message.message_id, country=country)
# ✅ عند وصول كود OTP
def send_otp_to_user(chat_id, number, otp):
    # قراءة ملف الرقم والدولة
    if os.path.exists(NUMBER_USER_FILE):
        with open(NUMBER_USER_FILE, "r") as f:
            data = json.load(f)
        country = data.get(number, {}).get("country", "غير معروف")
    else:
        country = "غير معروف"

    text = (
        "*تـــم اســـتلم كــــود جـــديــد ❤️🙈*\n\n"
        f"*الـــكـود الـــخاص بـك :* `{otp}`\n"
        f"*الـــرقـم الـــخاص بـك :* `{number}`\n"
        f"*الـــدولـــة :* {country}"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown")

# ✅ لوحة التحكم للأدمن
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ إضافة دولة جديدة", "🗑️ حذف دولة")
    markup.add("🌍 عرض الدول المتاحة")
    bot.send_message(message.chat.id, "👨‍💻 لوحة التحكم", reply_markup=markup)

# ✅ إضافة دولة
@bot.message_handler(func=lambda m: m.text == "➕ إضافة دولة جديدة")
def ask_country_name(message):
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(message.chat.id, "أرسل اسم الدولة التي تريد إضافتها:")
    bot.register_next_step_handler(msg, get_country_name)

def get_country_name(message):
    country = message.text.strip()
    msg = bot.send_message(message.chat.id, f"أرسل ملف CSV يحتوي على الأرقام الخاصة بدولة {country}:")
    bot.register_next_step_handler(msg, save_country_file, country)

def save_country_file(message, country):
    if not message.document:
        bot.send_message(message.chat.id, "❌ لم يتم إرسال ملف.")
        return
    file_info = bot.get_file(message.document.file_id)
    downloaded = bot.download_file(file_info.file_path)
    file_path = os.path.join(DATA_FOLDER, f"{country}.csv")
    with open(file_path, "wb") as f:
        f.write(downloaded)
    with open(file_path, "r") as f:
        total = len(f.readlines())
    bot.send_message(message.chat.id, f"✅ تم إضافة الدولة {country} وعدد {total} رقم.")

# ✅ حذف دولة
@bot.message_handler(func=lambda m: m.text == "🗑️ حذف دولة")
def delete_country_step(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".csv"):
            markup.add(filename.replace(".csv", ""))
    bot.send_message(message.chat.id, "اختر الدولة التي تريد حذفها:", reply_markup=markup)
    bot.register_next_step_handler(message, delete_country_file)

def delete_country_file(message):
    country = message.text.strip()
    file_path = os.path.join(DATA_FOLDER, f"{country}.csv")
    if os.path.exists(file_path):
        os.remove(file_path)
        bot.send_message(message.chat.id, f"✅ تم حذف الدولة {country}")
    else:
        bot.send_message(message.chat.id, "❌ لم يتم العثور على الملف.")

# ✅ عرض الدول المتاحة
@bot.message_handler(func=lambda m: m.text == "🌍 عرض الدول المتاحة")
def show_countries(message):
    countries = [f.replace(".csv", "") for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
    if countries:
        bot.send_message(message.chat.id, "🌍 الدول المتاحة:\n" + "\n".join(f"• {c}" for c in countries))
    else:
        bot.send_message(message.chat.id, "❌ لا توجد دول حالياً.")

# ✅ إشعار دخول مستخدم جديد
@bot.message_handler(func=lambda m: m.text == "/start")
def notify_admin_user_join(message):
    user = message.from_user
    name = user.first_name
    username = f"@{user.username}" if user.username else "لا يوجد"
    count = sum(1 for _ in open(__file__, 'r'))  # مثال مبسط لعدد المستخدمين
    bot.send_message(ADMIN_ID, f"🟢 تم دخول شخص جديد\nاسم العضو: {name}\nيوزر العضو: {username}")

# ✅ تشغيل البوت
# عند إرسال /Albrans من الأدمن
@bot.message_handler(commands=['Albrans'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📊 الإحصائيات", "🌍 عرض الدول")
    markup.add("📢 إرسال رسالة جماعية", "🔙 الرجوع")
    bot.send_message(message.chat.id, "👨‍💻 مرحبًا بك في لوحة تحكم Albrans", reply_markup=markup)

# تنفيذ أوامر الأدمن
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID)
def handle_admin_actions(message):
    if message.text == "📊 الإحصائيات":
        users = read_users()
        num_users = len(users)
        num_countries = len([f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")])
        total_numbers = sum(count_lines(os.path.join(DATA_FOLDER, f)) for f in os.listdir(DATA_FOLDER) if f.endswith(".csv"))

        text = (
            "📈 *إحصائيات البوت:*\n\n"
            f"👥 عدد المستخدمين: *{num_users}*\n"
            f"🌍 عدد الدول: *{num_countries}*\n"
            f"📱 عدد الأرقام المتاحة: *{total_numbers}*"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown")

    elif message.text == "🌍 عرض الدول":
        countries = [f.replace(".csv", "") for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
        if not countries:
            bot.send_message(message.chat.id, "❌ لا توجد دول حالياً.")
        else:
            text = "🌍 *الدول المتاحة حالياً:*\n\n" + "\n".join([f"• {c}" for c in countries])
            bot.send_message(message.chat.id, text, parse_mode="Markdown")

    elif message.text == "📢 إرسال رسالة جماعية":
        msg = bot.send_message(message.chat.id, "📝 أرسل الرسالة التي تريد إرسالها للمستخدمين:")
        bot.register_next_step_handler(msg, broadcast_message)

    elif message.text == "🔙 الرجوع":
        admin_panel(message)

# دالة إرسال جماعي
def broadcast_message(message):
    users = read_users()
    success, failed = 0, 0
    for uid in users:
        try:
            bot.send_message(uid, message.text)
            success += 1
        except:
            failed += 1
    bot.send_message(message.chat.id, f"✅ أُرسلت إلى {success} ✅\n❌ فشلت في {failed} ❌")

# تسجيل المستخدمين تلقائيًا
@bot.message_handler(commands=['start'])
def start_handler(message):
    user_id = message.chat.id
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w").close()
    with open(USERS_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(str(user_id) + "\n")
        name = message.from_user.first_name
        username = f"@{message.from_user.username}" if message.from_user.username else "لا يوجد"
        count = len(users) + 1
        bot.send_message(ADMIN_ID, f"🟢 دخول جديد:\n👤 {name}\n🔗 {username}\n👥 عدد الأعضاء: {count}")

    # (ضع هنا باقي رسالة الترحيب العادية بعد /start)

# أدوات مساعدة
def read_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return [int(x.strip()) for x in f if x.strip().isdigit()]

def count_lines(path):
    with open(path, "r") as f:
        return len(f.readlines())
print("🤖 Bot is starting albrans...")
@bot.message_handler(func=lambda m: True, content_types=["text"])
def monitor_otp_messages(message):
    if message.chat.type not in ["supergroup", "group"]:
        return

    if message.chat.username != "HK_OTP_RECEIVER":
        return

    text = message.text

    if not os.path.exists(NUMBER_USER_FILE):
        return

    with open(NUMBER_USER_FILE, "r") as f:
        number_user = json.load(f)

    found_number = None
    for number in number_user:
        if number in text:
            found_number = number
            break

    if found_number:
        user_info = number_user[found_number]
        user_id = user_info["user_id"] if isinstance(user_info, dict) else user_info
        country = user_info.get("country") if isinstance(user_info, dict) else None
        otp = extract_otp(text)
        if otp:
            send_otp_to_user(user_id, found_number, otp, country)
def assign_number_core(chat_id, message_id, country):
    file_path = os.path.join(DATA_FOLDER, f"{country}.csv")

    if not os.path.exists(file_path):
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ لم يتم العثور على أرقام.", parse_mode="Markdown")
        return

    with open(file_path, "r") as f:
        lines = f.readlines()

    if not lines:
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ لا توجد أرقام متوفرة حالياً.", parse_mode="Markdown")
        return

    number = lines.pop(0).strip()

    with open(file_path, "w") as f:
        f.writelines(lines)

    if not os.path.exists(NUMBER_USER_FILE):
        with open(NUMBER_USER_FILE, "w") as f:
            json.dump({}, f)

    with open(NUMBER_USER_FILE, "r") as f:
        data = json.load(f)

    data[number] = {
        "user_id": chat_id,
        "country": country
    }

    with open(NUMBER_USER_FILE, "w") as f:
        json.dump(data, f)

    text = (
        "*تـم تغيـير رقـمك بنجـاح 🔁*\n\n"
        f"*الـرقـــــم :* `{number}`\n"
        f"*الـدولـة :* {country}\n"
        "*الـتـطـبـيـق :* whatsapp\n"
        "*الـحـالـة :* فـــي الإنـتـظـار ❗️."
    )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("تغيير الرقم ⚡😔", callback_data=f"change_{country}"))

    bot.edit_message_text(chat_id=chat_id,
                          message_id=message_id,
                          text=text,
                          parse_mode="Markdown",
                          reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: call.data.startswith("change_"))
def handle_change_number(call):
    country = call.data.split("_", 1)[1]
    assign_number_core(chat_id=call.message.chat.id, message_id=call.message.message_id, country=country)
bot.infinity_polling(timeout=60, long_polling_timeout=60)
