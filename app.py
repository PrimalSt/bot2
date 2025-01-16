from flask import Flask, request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from aiogram import Dispatcher, Bot
from aiogram.webhook.aiohttp_server import setup_application
from aiohttp import web
import random
import os
import asyncio



TOKEN = os.getenv('TOKEN')  # Используем переменные окружения для безопасности

app = Flask(__name__)
# Создаем объект приложения для работы с Telegram API
application = Application.builder().token(TOKEN).build()
if not TOKEN:
    raise ValueError("Токен не задан. Проверьте переменную окружения TOKEN.")

async def on_startup(dp: Dispatcher):
    await bot.set_webhook(f"https://https://bot2-ksjg.onrender.com/webhook")

async def on_shutdown(dp: Dispatcher):
    await bot.delete_webhook()

app = web.Application()
dp = Dispatcher()
bot = Bot(token="7717648561:AAELGQaKsOQNaNDu3u7gOUTX9AvlBYoqPVc")

app.router.add_post("/webhook", dp.webhook_handler)


application.run_polling()

async def start(update: Update, context=None):
    keyboard = [
        [InlineKeyboardButton("Сыграть", callback_data='play')],
        [InlineKeyboardButton("Правила", callback_data='rules')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Добро пожаловать в казино! Выберите действие:", reply_markup=reply_markup)

async def play(update: Update, context=None):
    result = random.choice(["Вы выиграли!", "Вы проиграли!"])
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Результат игры: {result}")

async def rules(update: Update, context=None):
    rules_text = (
        "Правила игры в казино:\n"
        "1. Каждый раунд — случайный выбор выигрыша или проигрыша.\n"
        "2. Попробуйте удачу и играйте ответственно!"
    )
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=rules_text)

# Регистрация обработчиков
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(play, pattern='play'))
application.add_handler(CallbackQueryHandler(rules, pattern='rules'))

@app.route("/webhook", methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return 'ok', 200
    


if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=5000) # Привязываем приложение ко всем интерфейсам