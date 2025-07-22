import os
import json
import asyncio
import random
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- تنظیمات ---
BOT_TOKEN = "7518391763:AAF8A7Q4pIck46vOAZlKSOhcewy4FTbGLb8"
ADMIN_ID = 7031211787
DATA_FILE = "referrals.json"

REQUIRED_CHANNELS = [
    "@NeuroFi_Channel",
    "@Neuro_Fi",
    "@Neurofi_signals",
    "@Neurofi_Crypto"
]

REWARDS = [
    {"title": "🎨 NFT 50 دلاری", "count": 10, "weight": 2},
    {"title": "🎨 NFT 100 دلاری", "count": 5, "weight": 1},
    {"title": "🎨 NFT 150 دلاری", "count": 5, "weight": 1},
    {"title": "🪙 1,000 ECG Token", "count": 500, "weight": 15},
    {"title": "🐶 2,000 شیبا", "count": 50, "weight": 15},
    {"title": "💎 اکانت پریمیوم تلگرام", "count": 10, "weight": 3},
    {"title": "🌟 استار تلگرام", "count": 20, "weight": 3},
    {"title": "🎮 خدمات رایگان NeuroFi", "count": None, "weight": 30},
    {"title": "❌ امتیاز وفاداری بدون جایزه", "count": None, "weight": 90}
]

logging.basicConfig(level=logging.INFO)

# --- مدیریت فایل داده ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# --- بررسی عضویت در کانال‌ها ---
async def check_membership(user_id):
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={channel}&user_id={user_id}"
        response = requests.get(url).json()
        status = response.get("result", {}).get("status", "")
        if status not in ["member", "administrator", "creator"]:
            return channel
    return True

# --- قرعه‌کشی جایزه ---
def pick_reward():
    available = [r for r in REWARDS if r["count"] is None or r["count"] > 0]
    weights = [r["weight"] for r in available]
    reward = random.choices(available, weights=weights, k=1)[0]
    if reward["count"] is not None:
        reward["count"] -= 1
    return reward["title"]

# --- دستور /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.username or "ندارد"
    data = load_data()

    if user_id not in data:
        data[user_id] = {"wallet": "", "invited": 0, "spins": 0}
        save_data(data)

    membership = await check_membership(user_id)
    if membership is not True:
        await update.message.reply_text(
            f"⛔️ شما در کانال {membership} عضو نیستید.\nلطفاً عضو شوید و سپس /start را بزنید.")
        return

    # پیام خوش‌آمد کاستوم‌شده
    await update.message.reply_text(
        "🧠 به <b>شبکه بزرگ NeuroFi</b> خوش آمدید!\n\n"
        "💱 خدمات صرافی | 🎯 سیگنال‌های مبتنی بر هوش مصنوعی\n"
        "🧠 آموزش‌های کمیک و ویدئویی | 🎵 موزیک‌های مخصوص تریدرها\n"
        "💬 ویس‌چت تحلیلی و جلسات گفتگو با شرکت‌های بزرگ\n\n"
        "🔐 برای دریافت جایزه اول، گردونه برای شما فعال شد!",
        parse_mode="HTML"
    )

    await update.message.reply_sticker("CAACAgIAAxkBAAEHzPxlr17eY2hTT13EBgABoNQbYB18mS0AAfATAAKz-fFLMy7brKHQgJ8zBA")
    await asyncio.sleep(2)
    await update.message.reply_text("🎰 گردونه در حال چرخش است... لطفاً منتظر بمانید ⏳")
    await asyncio.sleep(3)

    reward = pick_reward()
    data[user_id]["spins"] += 1
    data[user_id]["last_reward"] = reward
    save_data(data)

    await update.message.reply_text(
        f"🎉 تبریک! شما برنده شدید:\n<b>{reward}</b>\n\n"
        "🔐 لطفاً آدرس کیف پول خود را با فرمت زیر بفرستید:\n"
        "`wallet: YOUR_ADDRESS (TRC20)`", parse_mode="HTML"
    )

    # پیام دعوت رفرال
    referral_link = f"https://t.me/{context.bot.username}?start={user_id}"
    referral_text = (
        "📢 <b>می‌خوای جوایز بیشتری بگیری؟</b>\n"
        "✅ دعوت کن:\n"
        "👥 ۵۰ نفر = گردونه دوم 🎁\n"
        "👥 ۱۵۰ نفر = گردونه سوم 🎯\n\n"
        f"🔗 لینک دعوت شما:\n{referral_link}"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📨 اشتراک‌گذاری لینک دعوت", url=referral_link)]
    ])
    await update.message.reply_text(referral_text, reply_markup=keyboard, parse_mode="HTML")

# --- دریافت کیف پول و ارسال به ادمین ---
async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()
    data = load_data()

    if not text.startswith("wallet:"):
        await update.message.reply_text("❗️ لطفاً آدرس کیف پول را با فرمت `wallet: YOUR_ADDRESS` ارسال کنید.", parse_mode="Markdown")
        return

    address = text.replace("wallet:", "").strip()
    data[user_id]["wallet"] = address
    save_data(data)

    reward = data[user_id].get("last_reward", "نامشخص")
    username = update.effective_user.username or "ندارد"
    msg = (
        f"🎁 کاربر جدید جایزه دریافت کرد:\n\n"
        f"🆔 آیدی: <code>{user_id}</code>\n"
        f"👤 یوزرنیم: @{username}\n"
        f"🎁 جایزه: {reward}\n"
        f"💼 آدرس کیف پول: <code>{address}</code>"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg, parse_mode="HTML")
    await update.message.reply_text("✅ آدرس ذخیره شد و برای تیم ارسال شد.")

# --- اجرا ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
    app.run_polling()
