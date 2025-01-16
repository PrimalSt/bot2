from flask import Flask, request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import random
import os
import asyncio

TOKEN = os.getenv('TOKEN')  # Используем переменные окружения для безопасности

app = Flask(__name__)

# Создаем объект приложения для работы с Telegram API
application = Application.builder().token(TOKEN).build()
if not TOKEN:
    raise ValueError("Токен не задан. Проверьте переменную окружения TOKEN.")

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
    
@app.route("/", methods=['GET'])
def index():
    return "Сервер работает и принимает запросы."

application.run_polling()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Используем порт из переменной окружения
    app.run(host="0.0.0.0", port=port)  # Привязываем приложение ко всем интерфейсам