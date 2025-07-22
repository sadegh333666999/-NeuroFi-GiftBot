import os
import json
import random
import asyncio
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "7518391763:AAF8A7Q4pIck46vOAZlKSOhcewy4FTbGLb8"
DATA_FILE = "referrals.json"
ADMIN_ID = 7031211787

REQUIRED_CHANNELS = [
    "@NeuroFi_Channel",
    "@Neuro_Fi",
    "@Neurofi_signals",
    "@Neurofi_Crypto"
]

REWARDS = [
    "🎨 NFT 50 دلاری",
    "🎨 NFT 100 دلاری",
    "🎨 NFT 150 دلاری",
    "🪙 1000 ECG توکن",
    "🐶 2000 شیبا",
    "💎 پریمیوم تلگرام 1 ماهه",
    "🌟 استار تلگرام",
    "🎮 استفاده رایگان از خدمات NeuroFi"
]

# ---------------- فایل داده ----------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ---------------- بررسی عضویت ----------------
async def check_membership(user_id):
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={channel}&user_id={user_id}"
        response = requests.get(url).json()
        status = response.get("result", {}).get("status", "")
        if status not in ["member", "administrator", "creator"]:
            return False
    return True

# ---------------- /start ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_member = await check_membership(user.id)

    welcome = (
        "🧠 <b>به دنیای <u>NeuroFi</u> خوش آمدید!</b>\n\n"
        "🎯 <b>ما یک شبکه اجتماعی واقعی هستیم!</b>\n\n"
        "📊 تحلیل بازار | 🤖 سیگنال‌ هوشمند | 🎙 ویس چت آموزشی\n"
        "🎮 خدمات رایگان | 📢 اخبار اقتصادی | 💸 صرافی حواله\n\n"
        "🚀 برای دریافت جوایز از گردونه شانس:\n"
        "1️⃣ در تمام کانال‌ها عضو شوید\n"
        "2️⃣ دکمه بررسی عضویت را بزنید\n"
        "3️⃣ گردونه را بچرخانید و جایزه بگیرید!\n\n"
        "<i>🎁 همه جوایز واقعی هستند!</i>"
    )

    await update.message.reply_text(
        welcome,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📡 کانال رسمی", url="https://t.me/NeuroFi_Channel")],
            [InlineKeyboardButton("📊 تحلیل و اطلاعیه", url="https://t.me/Neuro_Fi")],
            [InlineKeyboardButton("🎯 سیگنال‌ها", url="https://t.me/Neurofi_signals")],
            [InlineKeyboardButton("🪙 پروژه‌های کریپتو", url="https://t.me/Neurofi_Crypto")],
            [InlineKeyboardButton("✅ بررسی عضویت و شروع گردونه", callback_data="spin_check")]
        ])
    )

# ---------------- جایزه رندوم ----------------
def pick_reward():
    return random.choice(REWARDS)

# ---------------- تابع گردونه ----------------
async def spin_wheel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    await update.callback_query.answer()
    await update.callback_query.message.reply_sticker("CAACAgQAAxkBAAEFZ6Zl7fxWD7gP-FakeSpinSticker")
    await asyncio.sleep(2)
    await update.callback_query.message.reply_text("🎰 در حال چرخاندن گردونه...")
    await asyncio.sleep(3)

    reward = pick_reward()

    await update.callback_query.message.reply_text(
        f"🎉 تبریک {user.first_name}!\nشما برنده شدید:\n<b>{reward}</b>\n\n"
        "برای دریافت جایزه، با پشتیبانی تماس بگیرید 👇",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📩 ارتباط با پشتیبانی", url="https://t.me/NeuroFi_Persian")]
        ])
    )

    # ذخیره برای ارسال بعداً به ادمین (در صورت نیاز)
    data = load_data()
    uid = str(user.id)
    if uid not in data:
        data[uid] = {}
    data[uid]["last_reward"] = reward
    save_data(data)

# ---------------- هندل کال‌بک بررسی عضویت ----------------
async def check_spin_permission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    is_member = await check_membership(user.id)

    if not is_member:
        await query.answer()
        await query.message.reply_text("❗️شما هنوز در همه‌ی کانال‌ها عضو نشده‌اید. لطفاً عضو شوید.")
        return

    await spin_wheel(update, context)

# ---------------- اجرای ربات ----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, start))
    app.add_handler(CommandHandler("spin", spin_wheel))
    app.add_handler(CommandHandler("check", check_spin_permission))
    app.add_handler(MessageHandler(filters.COMMAND, start))
    app.add_handler(telegram.ext.CallbackQueryHandler(check_spin_permission, pattern="^spin_check$"))
    app.run_polling()
