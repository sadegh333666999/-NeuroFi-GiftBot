import os
import json
import random
import asyncio
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# تنظیمات توکن و ادمین
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 123456789  # آیدی عددی ادمین را اینجا قرار دهید

# فایل ذخیره‌سازی
DATA_FILE = "referrals.json"

# لیست کانال‌ها
REQUIRED_CHANNELS = [
    "@NeuroFi_Channel",
    "@Neuro_Fi",
    "@Neurofi_signals",
    "@Neurofi_Crypto"
]

# لیست جوایز
REWARDS = [
    {"title": "🎁 NFT ۵۰ دلاری", "count": 10, "weight": 2},
    {"title": "🎁 NFT ۱۵۰ دلاری", "count": 5, "weight": 1},
    {"title": "🪙 1,000 ECG توکن", "count": 500, "weight": 10},
    {"title": "🐶 2,000 شیبا", "count": 50, "weight": 10},
    {"title": "💎 اکانت پریمیوم تلگرام", "count": 10, "weight": 2},
    {"title": "🌟 استار تلگرام", "count": 20, "weight": 2},
    {"title": "🎮 استفاده رایگان از خدمات NeuroFi", "count": None, "weight": 30},
    {"title": "❌ جایزه‌ای تعلق نگرفت", "count": None, "weight": 50},
]

# بارگیری داده
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# ذخیره داده
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# بررسی عضویت
async def check_membership(user_id):
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={channel}&user_id={user_id}"
        res = requests.get(url).json()
        status = res.get("result", {}).get("status", "")
        if status not in ["member", "administrator", "creator"]:
            return channel
    return True

# انتخاب جایزه
def pick_reward():
    available = [r for r in REWARDS if r["count"] is None or r["count"] > 0]
    weights = [r["weight"] for r in available]
    selected = random.choices(available, weights=weights, k=1)[0]
    if selected["count"]:
        selected["count"] -= 1
    return selected["title"]

# پیام استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.username or "بدون_یوزرنیم"

    check = await check_membership(user_id)
    if check is not True:
        await update.message.reply_text(
            f"❌ شما هنوز در کانال یا گروه {check} عضو نشده‌اید.\nبرای دریافت جایزه لطفاً عضو شوید و مجدد /start بزنید."
        )
        return

    # پیام خوش‌آمد کاستوم
    welcome_text = """
🧠 <b>به دنیای <u>NeuroFi</u> خوش آمدید!</b>

🌐 ما فقط رسانه نیستیم! ما یک شبکه‌ی اجتماعی واقعی برای اقتصاد نوین هستیم!

📦 خدمات:
▪️ صرافی حواله و انتقال بین‌المللی
▪️ سیگنال شخصی‌سازی‌شده با هوش مصنوعی (NDS + تحلیل تکنیکال)
▪️ آموزش و مقاله‌های ارز دیجیتال
▪️ تحلیل وایت‌پیپر پروژه‌ها
▪️ گفت‌وگوی آزاد در گروه‌ها
▪️ حمله‌های توییتری جهت حمایت از پروژه‌ها
▪️ ویس چت تحلیلی، آموزشی و مصاحبه با پروژه‌های جهانی مثل Polygon

📋 برای دریافت جایزه، عضو کانال‌ها و گروه‌ها شوید:

📢 @NeuroFi_Channel
📍 @Neuro_Fi
🪙 @Neurofi_Crypto
🎯 @Neurofi_signals

🎁 لیست جوایز گردونه:
- NFT تا ۱۵۰ دلار
- ECG Token
- شیبا اینو
- اکانت پریمیوم تلگرام
- خدمات رایگان NeuroFi

✨ در جهان ما... جاذبه همیشه به سمت بالاست 🚀
"""
    await update.message.reply_text(welcome_text, parse_mode="HTML")

    await asyncio.sleep(2)
    await update.message.reply_animation("https://media.giphy.com/media/kJJqC6D2k8TVa/giphy.gif")  # گیف گردونه
    await asyncio.sleep(4)

    reward = pick_reward()
    await update.message.reply_text(f"🎉 تبریک! شما برنده شدید:\n\n🎁 <b>{reward}</b>", parse_mode="HTML")
    await update.message.reply_text("💼 لطفاً آدرس کیف پول USDT (TRC20) خود را ارسال کنید:")

    # ذخیره در دیتابیس
    data = load_data()
    user_id_str = str(user_id)
    if user_id_str not in data:
        data[user_id_str] = {}
    data[user_id_str]["username"] = username
    data[user_id_str]["reward"] = reward
    save_data(data)

# آدرس کیف پول
async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    wallet = update.message.text.strip()

    data = load_data()
    if user_id not in data:
        await update.message.reply_text("⚠️ ابتدا /start را بزنید.")
        return

    data[user_id]["wallet"] = wallet
    save_data(data)

    # ارسال برای ادمین
    msg = (
        f"📥 جایزه جدید ثبت شد!\n"
        f"👤 @{data[user_id].get('username')}\n"
        f"🎁 جایزه: {data[user_id].get('reward')}\n"
        f"💼 کیف پول: {wallet}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    await update.message.reply_text("✅ آدرس شما ثبت شد. تیم ما به زودی با شما تماس خواهد گرفت.")

# اجرای برنامه
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
    app.run_polling()
