import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Sticker
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
)
import random
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = "7031211787"  # آیدی عددی ادمین

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# لیست جوایز
PRIZES = [
    "🎁 50 دلار نقدی",
    "🎉 10 هزار توکن شیبا",
    "💎 NFT ویژه",
    "🚀 اکانت پرمیوم NeuroFi",
    "🧠 دسترسی به سیگنال حرفه‌ای",
    "🎬 دوره ویدیویی رایگان",
    "💰 500 توکن ECG",
    "🎧 موزیک اختصاصی تریدر",
]

# استیکر گردونه (می‌توانید استیکرهای بیشتری اضافه کنید)
WHEEL_STICKER = "CAACAgUAAxkBAAEF2_dlmrVLkP1LdEXX9gaYzvowG-hvUgACNAIAAk77cFVx1Erhw-kAzjQE"

# استارت
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎯 ورود به مرحله اول", callback_data="phase1")]
    ]
    await update.message.reply_text(
        "🧠 به دنیای *NeuroFi* خوش آمدید!\n\n"
        "📌 ما یک شبکه واقعی هستیم با:\n"
        "• خدمات صرافی و انتقال رمزارز\n"
        "• سیگنال هوش مصنوعی و شخصی‌سازی شده\n"
        "• تحلیل، مقاله، اخبار، وایت‌پیپر\n"
        "• ویس‌چت آموزشی، تحلیلی و مصاحبه با پروژه‌ها\n\n"
        "✨ در دنیای ما... جاذبه همیشه به سمت بالاست 🚀\n\n"
        "🎯 برای استفاده از گردونه، روی دکمه زیر بزنید\n"
        "📌 و جوایز ارزشمند مثل NFT، ارز دیجیتال و خدمات دریافت کن!",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

# بررسی مرحله 1
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "phase1":
        keyboard = [
            [InlineKeyboardButton("📢 کانال اصلی", url="https://t.me/NeuroFi_Channel")],
            [InlineKeyboardButton("📡 سیگنال‌ها", url="https://t.me/Neurofi_signals")],
            [InlineKeyboardButton("🧪 گروه تحلیل", url="https://t.me/Neuro_Fi")],
            [InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_membership")]
        ]
        await query.edit_message_text(
            "✅ لطفاً در کانال‌های زیر عضو شوید و سپس دکمه بررسی را بزنید:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "check_membership":
        await query.edit_message_text("🎰 در حال چرخاندن گردونه ... لطفا صبر کنید ...")
        await context.bot.send_sticker(chat_id=query.message.chat_id, sticker=WHEEL_STICKER)

        prize = random.choice(PRIZES)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"🎉 تبریک! شما برنده شدید:\n{prize}\n\n"
                 "💼 لطفاً آدرس کیف پول USDT (TRC20) خود را ارسال کنید.",
        )

        # اطلاع به ادمین
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🎁 کاربر @{query.from_user.username or query.from_user.id} برنده شد:\n{prize}"
        )

        # دکمه‌های مرحله بعد
        keyboard = [
            [InlineKeyboardButton("📨 دریافت لینک دعوت", callback_data="ref_link")],
            [InlineKeyboardButton("🎯 مرحله دوم (اد 100 نفر)", callback_data="phase2")]
        ]
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="📢 با دعوت از دوستان، جوایز بیشتری بگیر!\nهرچه بیشتر دعوت کنید، هدیه بزرگ‌تری دریافت می‌کنید 🎁",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "ref_link":
        invite_link = "https://t.me/Neuro_Fi?start={}".format(update.effective_user.id)
        await query.edit_message_text(
            f"🔗 لینک دعوت اختصاصی شما:\n{invite_link}\n\n"
            "📣 با دعوت دوستان، هدیه بگیر!",
        )

    elif query.data == "phase2":
        await query.edit_message_text(
            "✅ لطفاً 100 نفر به گروه اصلی @Neuro_Fi اضافه کن\n"
            "سپس دکمه زیر را بزن تا گردونه فعال شود.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎰 چرخاندن گردونه جایزه دوم", callback_data="check_100")]
            ])
        )

    elif query.data == "check_100":
        await context.bot.send_message(chat_id=query.message.chat_id, text="🎰 گردونه دوم در حال چرخش ...")
        await context.bot.send_sticker(chat_id=query.message.chat_id, sticker=WHEEL_STICKER)

        prize = random.choice(PRIZES)
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"🎊 برنده مرحله دوم شدی:\n{prize}\n\n"
                 "💼 آدرس کیف پولت رو بفرست تا جایزه رو بگیری.",
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🏆 برنده مرحله دوم: @{query.from_user.username or query.from_user.id}\n{prize}"
        )

# اجرای بات
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()
