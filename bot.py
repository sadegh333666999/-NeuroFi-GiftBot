import os
import random
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import requests

# تنظیمات اولیه
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "referrals.json"
ADMIN_ID = 123456789  # ID ادمین ربات

# لیست کانال‌ها و گروه‌ها برای بررسی عضویت
REQUIRED_CHANNELS = [
    "@NeuroFi_Channel",
    "@Neuro_Fi",
    "@Neurofi_signals",
    "@Neurofi_Crypto"
]

# جوایز با محدودیت منابع
REWARDS = [
    {"title": "🎨 NFT 50 دلاری", "count": 10, "weight": 2},
    {"title": "🎨 NFT 100 دلاری", "count": 5, "weight": 1},
    {"title": "🎨 NFT 150 دلاری", "count": 5, "weight": 1},
    {"title": "🪙 1,000 ECG Token", "count": 500, "weight": 15},  # 500*1000 = 500,000
    {"title": "🐶 2,000 شیبا", "count": 50, "weight": 15},        # 50*2,000 = 100,000
    {"title": "💎 اکانت پریمیوم تلگرام", "count": 10, "weight": 3},
    {"title": "🌟 استار تلگرام", "count": 20, "weight": 3},
    {"title": "🎮 خدمات رایگان NeuroFi", "count": None, "weight": 30},
    {"title": "❌ امتیاز وفاداری بدون جایزه", "count": None, "weight": 90}
]

# فایل ذخیره‌سازی داده‌ها
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# بررسی عضویت در کانال‌ها
async def check_membership(user_id):
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={channel}&user_id={user_id}"
        response = requests.get(url).json()
        status = response.get("result", {}).get("status", "")
        if status not in ["member", "administrator", "creator"]:
            return False
    return True

# پیام خوش‌آمد و عضویت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    is_member = await check_membership(user_id)

    # پیام خوش‌آمد
    welcome_text = """
    🧠 <b>به دنیای <u>NeuroFi</u> خوش آمدید!</b>\n
    📡 <i>رسانه‌ی هوشمند اقتصاد نوین</i>\n\n
    📊 تحلیل بازار | 🎯 سیگنال حرفه‌ای
    🎥 آموزش و کمیک‌استریپ | 💸 انتقال ارز
    🎶 موزیک و آرامش | 🪙 رمزارز و NFT\n
    ✨ <b>در جهان ما... جاذبه همیشه به سمت بالاست 🚀</b>
    """
    await update.message.reply_text(welcome_text, parse_mode="HTML")

    if not is_member:
        await update.message.reply_text("⛔️ برای فعال شدن گردونه لطفاً ابتدا در تمام کانال‌های بالا عضو شوید.")
        return

    # گردونه اول
    await update.message.reply_text("✅ عضویت شما تایید شد. گردونه اول فعال شد! 🎉")
    await update.message.reply_sticker("CAACAgQAAxkBAAEFZ6Zl7fxWD7gP-FakeSpinSticker")
    await asyncio.sleep(3)
    await update.message.reply_text("🎁 در حال چرخاندن گردونه... لطفاً منتظر بمانید...")
    await asyncio.sleep(5)
    await update.message.reply_text("🎉 تبریک! شما 5 تتر دریافت کردید. برای دریافت جایزه، آدرس کیف پول USDT (TRC20) را ارسال کنید.")

# انتخاب جایزه با محدودیت
def pick_reward():
    available = [r for r in REWARDS if r["count"] is None or r["count"] > 0]
    weights = [r["weight"] for r in available]
    chosen = random.choices(available, weights=weights, k=1)[0]

    if chosen["count"] is not None:
        chosen["count"] -= 1

    return chosen["title"]

# گردونه دوم (۵۰ دعوت)
async def check_invites(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    invites = data.get(user_id, {}).get("invited", 0)

    if invites >= 50:
        reward = pick_reward()
        await update.message.reply_text(f"🎉 تبریک! شما ۵۰ نفر را دعوت کردید. گردونه دوم فعال شد!\n\n جایزه شما: {reward}")
        data[user_id]["spins"] += 1
        save_data(data)
    else:
        await update.message.reply_text(f"📣 هنوز {50 - invites} دعوت دیگر برای فعال شدن گردونه دوم باقی مانده است. ادامه بدهید!")

# گردونه سوم (۱۵۰ دعوت)
async def check_third_spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    data = load_data()
    invites = data.get(user_id, {}).get("invited", 0)

    if invites >= 150:
        reward = pick_reward()
        await update.message.reply_text(f"🎉 تبریک! شما ۱۵۰ نفر را دعوت کردید. گردونه سوم فعال شد!\n\n جایزه شما: {reward}")
        data[user_id]["spins"] += 1
        save_data(data)
    else:
        await update.message.reply_text(f"📣 هنوز {150 - invites} دعوت دیگر برای فعال شدن گردونه سوم باقی مانده است. ادامه بدهید!")

# ذخیره آدرس کیف پول و ارسال به ادمین
async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    wallet = update.message.text.strip()

    data = load_data()
    if user_id not in data:
        data[user_id] = {"invited": 0, "spins": 0, "wallet": "", "last_reward": ""}

    data[user_id]["wallet"] = wallet
    save_data(data)

    # ارسال به ادمین
    admin_msg = (
        f"📩 کاربر جدید جایزه دریافت کرد:\n"
        f"👤 یوزر: @{update.effective_user.username}\n"
        f"🆔 آیدی: {user_id}\n"
        f"🎁 جایزه: {data[user_id]['last_reward']}\n"
        f"💼 آدرس کیف پول: {wallet}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg)

    await update.message.reply_text("✅ آدرس کیف پول شما ذخیره شد و برای تیم ارسال شد.")

# اجرای ربات
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check_invite", check_invites))
    app.add_handler(CommandHandler("third_spin", check_third_spin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
    app.run_polling()
