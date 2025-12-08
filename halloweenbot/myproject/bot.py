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


async def edit_command(update: Update, context: CallbackContext):
    session.mode = "edit"
    text = load_message(session.mode)
    await send_photo(update, context, session.mode)
    await send_text(update, context, text)


async def edit_message(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id
    photo_path = f"resources/users/{user_id}/photo.jpg"

    if not os.path.exists(photo_path):
        await send_text(update, context, "Спочатку завантажте або створіть зображення")
        return
    prompt = load_prompt(session.mode)
    ai_edit_image(input_image_path=photo_path, prompt=prompt + text, output_path=photo_path)
    await send_photo(update, context, photo_path)


async def on_message(update: Update, context):
    if session.mode == "create":
        await create_message(update, context)
    elif session.mode == "edit":
        await edit_message(update, context)
    else:
        await send_text(update, context, "Привіт!")
        await send_text(update, context, "Ви написали " + update.message.text)


async def create_command(update, context):
    session.mode = "create"
    text = load_message(session.mode)
    await send_photo(update, context, session.mode)
    await send_text(update, context, text)

    await send_text_buttons(update, context, text, {
        "create_anime": "👧 Аніме",
        "create_photo": "📸 Фото"
    }, checkbox_key=session.image_type)


async def create_button(update: Update, context):
    await update.callback_query.answer()
    query = update.callback_query.data
    session.image_type = query
    text = load_message(session.mode)
    message = update.callback_query.message

    await edit_text_buttons(message, text, {
        "create_anime": "👧 Аніме",
        "create_photo": "📸 Фото"
    }, checkbox_key=session.image_type)


async def create_message(update: Update, context):
    text = update.message.text
    user_id = update.message.from_user.id
    photo_path = f"resources/users/{user_id}/photo.jpg"

    prompt = load_prompt(session.image_type)  # Використовуємо load_prompt замість load_message
    ai_create_image(prompt=prompt + text, output_path=photo_path)
    await send_photo(update, context, photo_path)


# Створюємо Telegram-бота
app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()
app.add_error_handler(error_handler)
session.mode = None
session.image_type = "create_anime"

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("image", create_command))
app.add_handler(CommandHandler("edit", edit_command))
app.add_handler(CallbackQueryHandler(create_button, pattern="^create_.*"))
app.run_polling()
