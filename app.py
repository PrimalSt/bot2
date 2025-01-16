from flask import Flask, request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import random
import os

TOKEN = os.getenv('TOKEN')  # Используем переменные окружения для безопасности

app = Flask(__name__)

# Создаем объект приложения для работы с Telegram API
application = Application.builder().token(TOKEN).build()

def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Сыграть", callback_data='play')],
        [InlineKeyboardButton("Правила", callback_data='rules')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Добро пожаловать в казино! Выберите действие:", reply_markup=reply_markup)

def play(update: Update, context):
    result = random.choice(["Вы выиграли!", "Вы проиграли!"])
    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Результат игры: {result}")

def rules(update: Update, context):
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

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    """Обработка обновлений, получаемых через вебхук."""
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return 'ok'

if __name__ == '__main__':
    app.run(port=8443)