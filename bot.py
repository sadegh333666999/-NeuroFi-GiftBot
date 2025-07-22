import os
import random
import json
import asyncio
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ---------------- تنظیمات اولیه ----------------
BOT_TOKEN = "توکن_ربات_شما_اینجا"  # یا os.getenv("BOT_TOKEN")
ADMIN_ID = 123456789  # آیدی عددی ادمین
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
    not_joined = []
    for channel in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={channel}&user_id={user_id}"
        response = requests.get(url).json()
        status = response.get("result", {}).get("status", "")
        if status not in ["member", "administrator", "creator"]:
            not_joined.append(channel)
    return not_joined

# ---------------- انتخاب جایزه ----------------
def pick_reward():
    available = [r for r in REWARDS if r["count"] is None or r["count"] > 0]
    weights = [r["weight"] for r in available]
    chosen = random.choices(available, weights=weights, k=1)[0]
    if chosen["count"] is not None:
        chosen["count"] -= 1
    return chosen["title"]

# ---------------- /start ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    data = load_data()

    if uid not in data:
        data[uid] = {"invited": 0, "spins": 0, "wallet": "", "last_reward": ""}
        save_data(data)

    # ذخیره دعوت
    if context.args:
        inviter = context.args[0]
        if inviter != uid and inviter in data:
            data[inviter]["invited"] += 1
            save_data(data)

    not_joined = await check_membership(user.id)

    intro = (
        "🧠 <b>به دنیای <u>NeuroFi</u> خوش آمدید!</b>\n\n"
        "ما یک شبکه اجتماعی تخصصی مالی و رمزارزی هستیم که شامل:\n"
        "📊 تحلیل بازار و سیگنال شخصی‌سازی‌شده با هوش مصنوعی\n"
        "🎥 آموزش، مصاحبه با پروژه‌ها و وایت‌پیپرخوانی\n"
        "💱 خدمات انتقال رمزارز، صرافی، بازی و پاداش\n\n"
        "📢 برای فعال شدن گردونه جوایز باید در کانال‌ها عضو شوید:\n"
        + "\n".join([f"🔹 {ch}" for ch in REQUIRED_CHANNELS])
    )

    await update.message.reply_text(intro, parse_mode="HTML")

    if not_joined:
        await update.message.reply_text("⛔️ ابتدا در همه‌ی کانال‌ها عضو شوید سپس /start بزنید.")
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎰 شروع گردونه جوایز", callback_data="spin")]
    ])
    await update.message.reply_text("✅ عضویت تأیید شد. برای استفاده از گردونه دکمه زیر را بزنید:", reply_markup=keyboard)

# ---------------- گردونه ----------------
async def spin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    uid = str(user.id)

    data = load_data()
    user_data = data.get(uid, {"invited": 0, "spins": 0, "wallet": "", "last_reward": ""})

    not_joined = await check_membership(user.id)
    if not_joined:
        await query.edit_message_text("⛔️ شما هنوز در برخی کانال‌ها عضو نیستید. لطفاً عضو شوید و دوباره تلاش کنید.")
        return

    invited = user_data.get("invited", 0)
    spins = user_data.get("spins", 0)
    allowed = (
        spins == 0 or
        (spins == 1 and invited >= 50) or
        (spins == 2 and invited >= 150)
    )

    if not allowed:
        needed = 50 if spins == 1 else 150
        await query.edit_message_text(f"⛔️ برای گردونه بعدی باید {needed} نفر را دعوت کنید.\n📨 دعوت فعلی شما: {invited}")
        return

    # چرخش گردونه
    await context.bot.send_sticker(chat_id=user.id, sticker="CAACAgUAAxkBAAEFZ7xl7x-LW1uknM_sGIFakeSpinSticker")
    await asyncio.sleep(4)
    await context.bot.send_message(chat_id=user.id, text="🎁 در حال چرخاندن گردونه...")
    await asyncio.sleep(3)

    reward = pick_reward()
    user_data["spins"] = spins + 1
    user_data["last_reward"] = reward
    data[uid] = user_data
    save_data(data)

    await context.bot.send_message(
        chat_id=user.id,
        text=f"🎉 تبریک! شما برنده شدید:\n\n<b>{reward}</b>\n\n"
             "لطفاً آدرس کیف پول خود را با فرمت زیر ارسال کنید:\n"
             "`wallet: YOUR_ADDRESS`\n(مثلاً برای USDT روی TRC20)",
        parse_mode="HTML"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🎁 کاربر جایزه دریافت کرد:\n"
             f"🆔 ID: {uid}\n"
             f"👤 @{user.username or 'بدون نام'}\n"
             f"🎁 جایزه: {reward}"
    )

# ---------------- کیف پول ----------------
async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text.strip()

    if not text.startswith("wallet:"):
        await update.message.reply_text("❗️لطفاً آدرس را با فرمت زیر وارد کنید:\n`wallet: YOUR_ADDRESS`", parse_mode="Markdown")
        return

    address = text.replace("wallet:", "").strip()
    data = load_data()

    if user_id not in data:
        data[user_id] = {"invited": 0, "spins": 0, "wallet": "", "last_reward": ""}

    data[user_id]["wallet"] = address
    save_data(data)

    await update.message.reply_text("✅ آدرس کیف پول ذخیره شد و برای تیم ارسال گردید.")

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📩 کیف پول دریافت شد:\n🆔 {user_id}\n📦 {address}"
    )

# ---------------- اجرای ربات ----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(spin_callback, pattern="^spin$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
    app.run_polling()
