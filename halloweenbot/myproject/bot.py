from requests import Session
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler, \
    CallbackContext
import os
import logging
from ai import *
from util import *

# тут будемо писати наш код :)
async def start(update: Update, context):
    session.mode = "main"

    text = load_message(session.mode)
    await send_photo(update, context, session.mode)
    await send_text(update, context, text)

    user_id = update.message.from_user.id
    create_user_dir(user_id)

    await show_main_menu(update, context, {
        "start": "🧟‍♂️ Головне меню бота",
        "image": "⚰️ Створюємо зображення",
        "edit": "🧙‍♂️ Змінюємо зображення",
        "merge": "🕷️ Об'єднуємо зображення",
        "party": "🎃 Фото для Halloween-вечірки",
        "video": "🎬☠️ Страшне Halloween-відео з фото"
    })

async def hello(update: Update,  context):
    await send_text(update, context, "Привіт!")
    await send_text(update, context, "Як ти, *друже*?")
    await send_text(update, context, f"Ти написав: {update.message.text}")

    buttons = {
        "start": "Запустити!",
        "stop" : "Зупинити!"
    }

    await send_text_buttons(update, context,"Кнопки:", buttons)

async def hello_button (update: Update, context):
    await update.callback_query.answer()
    data = update.callback_query.data
    if data == "start":
        await send_text(update, context, "Процес запущено!")
    elif data == "stop":
        await send_text(update, context, "Процес зупинено!")


# Створюємо Telegram-бота
app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
session.mode = None
app.add_error_handler(error_handler)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()
