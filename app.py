from flask import Flask, request
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, Dispatcher
import random

TOKEN = '7129325002:AAEPe4GSU_Utxu2aXIhXOM2THMAEbmbQeec'

app = Flask(__name__)
bot = Bot(token=TOKEN)

def start(update: Update, context):
    keyboard = [
        [InlineKeyboardButton("Сыграть", callback_data='play')],
        [InlineKeyboardButton("Правила", callback_data='rules')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Добро пожаловать в казино! Выберите действие:", reply_markup=reply_markup)

def play(update: Update, context):
    result = random.choice(["Вы выиграли!", "Вы проиграли!"])
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=f"Результат игры: {result}")

def rules(update: Update, context):
    rules_text = (
        "Правила игры в казино:\n"
        "1. Каждый раунд — случайный выбор выигрыша или проигрыша.\n"
        "2. Попробуйте удачу и играйте ответственно!"
    )
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=rules_text)

def handle_update(update: Update, context):
    dp = Dispatcher(bot, None, workers=0, use_context=True)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(play, pattern='play'))
    dp.add_handler(CallbackQueryHandler(rules, pattern='rules'))
    dp.process_update(update)

@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(), bot)
    handle_update(update, None)
    return 'ok'

if __name__ == '__main__':
    app.run(port=8443)