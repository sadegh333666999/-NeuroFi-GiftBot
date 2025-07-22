import os
import json
import random
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)
import requests

# ---------------- تنظیمات ----------------
BOT_TOKEN = "7518391763:AAF8A7Q4pIck46vOAZlKSOhcewy4FTbGLb8"
ADMIN_ID = 7031211787
DATA_FILE = "neuro_data.json"

REQUIRED_CHANNELS = [
    "@NeuroFi_Channel",
    "@Neuro_Fi",
    "@Neurofi_signals",
    "@Neurofi_Crypto"
]

REWARD_POOL = [
    "🎨 NFT به ارزش ۵۰ دلار",
    "🎨 NFT به ارزش ۱۰۰ دلار",
    "🎨 NFT به ارزش ۱۵۰ دلار",
    "🪙 ۵۰۰ ECG توکن",
    "🐶 ۲۰۰۰ شیبا",
    "💎 اکانت پریمیوم ۱ ماهه",
    "🌟 استار هدیه",
    "🎮 خدمات رایگان NeuroFi",
    "❌ امتیاز وفاداری بدون جایزه"
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
async def is_member(user_id):
    for ch in REQUIRED_CHANNELS:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={ch}&user_id={user_id}"
        result = requests.get(url).json()
        status = result.get("result", {}).get("status", "")
        if status not in ["member", "administrator", "creator"]:
            return False
    return True

# ---------------- پیام خوش‌آمد ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    data = load_data()

    # ذخیره رفرال
    if context.args:
        ref_id = context.args[0]
        if ref_id != uid:
            if uid not in data:
                data[uid] = {"ref": ref_id, "wallet": "", "spins": 0, "invites": 0}
            if ref_id in data:
                data[ref_id]["invites"] = data[ref_id].get("invites", 0) + 1
    else:
        if uid not in data:
            data[uid] = {"ref": "", "wallet": "", "spins": 0, "invites": 0}
    save_data(data)

    text = (
        "🧠 <b>به دنیای NeuroFi خوش آمدید!</b>\n\n"
        "🌐 شبکه اجتماعی ما ترکیبی از:\n"
        "💱 خدمات صرافی و حواله\n"
        "🎯 سیگنال‌های هوش مصنوعی شخصی‌سازی‌شده\n"
        "📰 اخبار اقتصادی + مقالات رمزارز\n"
        "💬 گروه گفت‌وگو، ویس چت، همکاری با پروژه‌ها\n\n"
        "🎁 جوایز در ۴ مرحله:\n"
        "1️⃣ عضویت در کانال‌ها = گردونه ۱\n"
        "2️⃣ اد ۱۰۰ نفر = گردونه ۲\n"
        "3️⃣ اد ۱۵۰ نفر = گردونه ۳\n"
        "4️⃣ اد ۲۰۰ نفر = گردونه ۴\n\n"
        "👇 ابتدا در این کانال‌ها عضو شوید:"
    )

    keyboard = [
        [InlineKeyboardButton("📢 NeuroFi Channel", url="https://t.me/NeuroFi_Channel")],
        [InlineKeyboardButton("📍 اطلاعیه و تحلیل", url="https://t.me/Neuro_Fi")],
        [InlineKeyboardButton("📡 سیگنال‌ها", url="https://t.me/Neurofi_signals")],
        [InlineKeyboardButton("🪙 پروژه‌های کریپتو", url="https://t.me/Neurofi_Crypto")],
        [InlineKeyboardButton("✅ بررسی عضویت و قرعه‌کشی", callback_data="verify")],
    ]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

# ---------------- بررسی عضویت و قرعه‌کشی ----------------
async def verify_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    uid = str(user.id)
    data = load_data()

    await query.answer("در حال بررسی عضویت...")

    if not await is_member(user.id):
        await query.edit_message_text("⛔️ در برخی از کانال‌ها هنوز عضو نیستید. لطفاً عضو شوید و دوباره امتحان کنید.")
        return

    # اگر مجاز به چرخش هست
    spins = data[uid]["spins"]
    invites = data[uid]["invites"]

    spin_allowed = (
        spins == 0 or
        (spins == 1 and invites >= 100) or
        (spins == 2 and invites >= 150) or
        (spins == 3 and invites >= 200)
    )

    if not spin_allowed:
        await query.edit_message_text("❗️شرایط لازم برای قرعه‌کشی بعدی را هنوز کامل نکردید.")
        return

    # چرخش گردونه
    await query.edit_message_text("🎰 در حال چرخاندن گردونه ... لطفاً منتظر بمانید.")
    await context.bot.send_sticker(chat_id=user.id, sticker="CAACAgUAAxkBAAIBm2W_YgY8S4AAAS2XxYv_xJcEcHo7Yr0AAikAA9C-MFUgVgaMJjYEVjQE")
    await asyncio.sleep(3)

    prize = random.choice(REWARD_POOL)
    data[uid]["spins"] += 1
    data[uid]["last_reward"] = prize
    save_data(data)

    msg = (
        f"🎉 تبریک! شما برنده شدید:\n<b>{prize}</b>\n\n"
        "📥 لطفاً آدرس کیف پول خود را با فرمت زیر ارسال کنید:\n\n"
        "`wallet: YOUR_WALLET_ADDRESS`\n\n"
        "🎯 پس از ارسال، جایزه برای شما رزرو خواهد شد.\n"
        f"📩 ارتباط با ادمین: @NeuroFi_Persian"
    )
    await context.bot.send_message(chat_id=user.id, text=msg, parse_mode="HTML")

# ---------------- آدرس کیف پول ----------------
async def handle_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = str(user.id)
    text = update.message.text.strip()
    data = load_data()

    if text.lower().startswith("wallet:"):
        address = text.split("wallet:")[1].strip()
        data[uid]["wallet"] = address
        save_data(data)

        # ارسال به ادمین
        reward = data[uid].get("last_reward", "ندارد")
        admin_text = (
            f"🎁 کاربر جدید جایزه گرفت:\n"
            f"👤 یوزرنیم: @{user.username}\n"
            f"🆔 آیدی: {uid}\n"
            f"🎉 جایزه: {reward}\n"
            f"💼 کیف پول: {address}"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)
        await update.message.reply_text("✅ آدرس شما ثبت شد و به ادمین ارسال شد.")
    else:
        await update.message.reply_text("❗️لطفاً با فرمت زیر ارسال کنید:\nwallet: YOUR_WALLET_ADDRESS")

# ---------------- اجرای ربات ----------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_membership, pattern="^verify$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_wallet))
    app.run_polling()
