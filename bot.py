import os
import json
import asyncio
import random
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# 🛡️ تنظیمات
BOT_TOKEN = "7518391763:AAF8A7Q4pIck46vOAZlKSOhcewy4FTbGLb8"
ADMIN_ID = 7031211787  # آیدی عددی ادمین
DATA_FILE = "referrals.json"

REQUIRED_CHANNELS = [
    "@NeuroFi_Channel",
    "@Neuro_Fi",
    "@Neurofi_signals",
    "@Neurofi_Crypto"
]

REWARDS = [
    {"title": "🎨 NFT 50 دلاری", "count": 10, "weight": 3},
    {"title": "🎨 NFT 100 دلاری", "count": 5, "weight": 2},
    {"title": "🎨 NFT 150 دلاری", "count": 5, "weight": 1},
    {"title": "🪙 1000 ECG", "count": 500, "weight": 10},
    {"title": "🐶 2000 شیبا", "count": 50, "weight": 10},
    {"title": "💎 پریمیوم تلگرام", "count": 10, "weight": 2},
    {"title": "🌟 استار تلگرام", "count": 20, "weight": 3},
    {"title": "🎮 خدمات رایگان NeuroFi", "count": None, "weight": 20},
    {"title": "📌 امتیاز وفاداری (بدون جایزه)", "count": None, "weight": 50}
]

# 📦 مدیریت فایل
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# 🔍 بررسی عضویت
async def check_membership(user_id):
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={channel}&user_id={user_id}"
        resp = requests.get(url).json()
        status = resp.get("result", {}).get("status", "")
        if status not in ["member", "administrator", "creator"]:
            return False, channel
    return True, ""

# 🎁 انتخاب جایزه
def pick_reward():
    available = [r for r in REWARDS if r["count"] is None or r["count"] > 0]
    weights = [r["weight"] for r in available]
    chosen = random.choices(available, weights=weights, k=1)[0]
    if chosen["count"]:
        chosen["count"] -= 1
    return chosen["title"]

# 🧠 استارت ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    data = load_data()

    if user_id not in data:
        data[user_id] = {"invited": 0, "wallet": "", "last_reward": "", "spins": 0}
        save_data(data)

    member, missing_channel = await check_membership(user.id)
    if not member:
        await update.message.reply_text(
            f"⛔️ برای استفاده از ربات، لطفاً ابتدا در کانال زیر عضو شوید:\n{missing_channel}"
        )
        return

    # 🎉 پیام خوش‌آمد + دکمه گردونه
    welcome = """🧠 به دنیای <b>NeuroFi</b> خوش آمدید!

📌 ما یک شبکه واقعی هستیم با:
• خدمات صرافی و انتقال رمزارز
• سیگنال هوش مصنوعی و شخصی‌سازی شده
• تحلیل‌، مقاله‌، اخبار، وایت‌پیپر
• ویس‌چت آموزشی، تحلیلی و مصاحبه با پروژه‌ها

✨ <b>در دنیای ما... جاذبه همیشه به سمت بالاست 🚀</b>

🎯 برای استفاده از گردونه، روی دکمه زیر بزنید.
📌 و جوایز ارزشمند مثل NFT، ارز دیجیتال و خدمات دریافت کن!
"""
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 گردونه شانس", callback_data="spin")]
    ])
    await update.message.reply_text(welcome, reply_markup=keyboard, parse_mode="HTML")

# 🎰 گردونه
async def spin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    user_id = str(user.id)

    data = load_data()
    if user_id not in data:
        await query.answer("❗️ لطفاً ابتدا /start را بزنید.")
        return

    member, missing = await check_membership(user.id)
    if not member:
        await query.answer()
        await query.message.reply_text(f"⛔️ هنوز عضو کانال {missing} نشده‌اید!")
        return

    await query.answer()
    await query.message.reply_sticker("CAACAgUAAxkBAAEFaehl8CLNx5g0H6P3sGy1zq-FAKpO4wACDAADwDZPEyMBfnRW_4e2LwQ")  # استیکر گردونه
    await asyncio.sleep(2)
    await query.message.reply_text("🔄 در حال چرخش گردونه...")
    await asyncio.sleep(3)

    reward = pick_reward()
    data[user_id]["last_reward"] = reward
    data[user_id]["spins"] += 1
    save_data(data)

    await query.message.reply_text(
        f"🎉 تبریک! شما برنده شدید:\n\n<b>{reward}</b>\n\n"
        "📩 لطفاً آدرس کیف پول خود را با فرمت زیر ارسال کنید:\n\n"
        "<code>wallet: YOUR_WALLET_ADDRESS</code>",
        parse_mode="HTML"
    )

# 💼 دریافت آدرس کیف پول
async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    text = update.message.text.strip()
    data = load_data()

    if not text.lower().startswith("wallet:"):
        await update.message.reply_text("📌 لطفاً آدرس کیف پول را با فرمت زیر ارسال کنید:\nwallet: YOUR_WALLET")
        return

    wallet = text.split("wallet:")[1].strip()
    if user_id not in data:
        await update.message.reply_text("❗️ لطفاً ابتدا /start را بزنید.")
        return

    data[user_id]["wallet"] = wallet
    save_data(data)

    # ارسال پیام به ادمین
    reward = data[user_id]["last_reward"]
    admin_msg = (
        f"🎁 کاربر جدید جایزه گرفت:\n\n"
        f"👤 Username: @{user.username or 'N/A'}\n"
        f"🆔 ID: {user_id}\n"
        f"🎁 جایزه: {reward}\n"
        f"💳 کیف پول: {wallet}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)
    await update.message.reply_text("✅ آدرس کیف پول ثبت شد و برای تیم پشتیبانی ارسال شد.")

# ▶️ اجرای ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(spin_callback, pattern="^spin$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
    app.run_polling()
