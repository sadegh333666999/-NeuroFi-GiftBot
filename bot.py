import random
import time
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, Filters

# اطلاعات شما
BOT_TOKEN = "توکن شما اینجا"
ADMIN_ID = 7031211787

# لیست جوایز
rewards = [
    "NFT اختصاصی 🎁",
    "۵ تتر USDT 🎉",
    "دسترسی VIP به سیگنال‌ها 🔐",
    "جایزه‌ای تعلق نگرفت ❌"
]

# مرحله اول /start
def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    context.bot.send_message(
        chat_id=chat_id,
        text="🧠 به دنیای NeuroFi خوش آمدید!\n\n"
             "📌 ما یک شبکه واقعی هستیم با:\n"
             "• خدمات صرافی و انتقال رمزارز\n"
             "• سیگنال‌های شخصی‌سازی‌شده با هوش مصنوعی\n"
             "• تحلیل اخبار، وایت‌پیپر و مقاله\n"
             "• مصاحبه با پروژه‌های بزرگ\n"
             "• ویس چت تحلیلی و آموزشی\n\n"
             "🎯 برای استفاده از گردونه، دکمه زیر رو بزن:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎰 گردونه شانس", callback_data="spin")]
        ])
    )

# گردونه شانس
def spin_wheel(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat.id
    query.answer()

    # ارسال گیف گردونه
    with open("spinner.gif", "rb") as gif:
        context.bot.send_animation(chat_id=chat_id, animation=gif)

    time.sleep(3)  # تأخیر برای نمایش گیف

    prize = random.choice(rewards)

    context.bot.send_message(chat_id=chat_id, text=f"🎉 تبریک! شما برنده شدید:\n\n🎁 {prize}")

    if "❌" not in prize:
        context.bot.send_message(chat_id=chat_id, text="💼 لطفاً آدرس کیف پول USDT (TRC20) خود را ارسال کنید:")

    # ارسال به ادمین
    user = query.from_user
    msg = f"👤 کاربر: {user.first_name} ({user.id})\n🎁 جایزه: {prize}"
    context.bot.send_message(chat_id=ADMIN_ID, text=msg)

# دریافت کیف پول
def handle_wallet(update: Update, context: CallbackContext):
    wallet = update.message.text
    user = update.message.from_user

    # ارسال برای ادمین
    msg = f"💳 کیف پول از {user.first_name} ({user.id}):\n{wallet}"
    context.bot.send_message(chat_id=ADMIN_ID, text=msg)

    update.message.reply_text("✅ آدرس کیف پول دریافت شد. تیم ما به زودی جایزه را بررسی می‌کند.")

# اجرای ربات
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(spin_wheel, pattern="^spin$"))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_wallet))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
