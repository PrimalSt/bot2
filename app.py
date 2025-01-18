import os
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.exceptions import TelegramAPIError
from aiogram.client.default import DefaultBotProperties
import logging
import sqlite3
from database import init_db, add_user, get_balance, update_balance
from flask import Flask, render_template, request, jsonify
import random
init_db()
app = Flask(__name__)

# Путь к базе данных
DB_PATH = "casino_bot.db"
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get token from environment variable with error handling
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что переменная BOT_TOKEN установлена.")

# Initialize bot and dispatcher with error handling
try:
      bot = Bot(token=TOKEN, session=AiohttpSession())
      dp = Dispatcher(bot=bot, storage=MemoryStorage())
except Exception as e:
      logger.error(f"Failed to initialize bot: {e}")
      raise

casino_web_app = WebAppInfo(url="https://bot2-ksjg.onrender.com")
web_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Перейти в Казино", web_app=casino_web_app)]
    ]
)

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    add_user(telegram_id=message.from_user.id, username=message.from_user.username)
    try:
        await bot.send_message(
            chat_id=message.chat.id,
            text=(
                "Welcome to Casino Bot! 🎰\n\n"
                "Ваш стартовый баланс: 1000."
            ),
            reply_markup=web_button
        )
    except TelegramAPIError as e:
        logger.error(f"Error in start_handler: {e}")
        await bot.send_message(chat_id=message.chat.id, text="Sorry, an error occurred. Please try again later.")

@dp.message(Command("balance"))
async def balance_handler(message: types.Message):
    balance = get_balance(telegram_id=message.from_user.id)
    if balance is not None:
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Ваш текущий баланс: {balance}"
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Вы не зарегистрированы. Используйте /start для регистрации."
        )
 
@dp.message(Command("add_balance"))
async def add_balance_handler(message: types.Message):
    update_balance(telegram_id=message.from_user.id, amount=500)
    new_balance = get_balance(telegram_id=message.from_user.id)
    await bot.send_message(
        chat_id=message.chat.id,
        text=f"Ваш баланс пополнен. Новый баланс: {new_balance}"
    )
# Обработчик для получения обновлений от Telegram

async def handle_webhook(request):
    try:
        json_data = await request.json()
        update = types.Update(**json_data)

        if update.message and update.message.text:
            message = update.message
            if message.text == "/start":
                await start_handler(message)
        
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return web.Response(status=500)

# Обработчик запуска приложения
async def on_startup(app: web.Application):
    try:
        webhook_url = "https://bot2-ksjg.onrender.com/webhook"
        await bot.set_webhook(webhook_url)
        logger.info("Webhook set successfully LOL")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        raise

# Обработчик завершения работы приложения
async def on_shutdown(app: web.Application):
    try:
        await bot.session.close()  # Закрытие сессии напрямую
#        await bot.delete_webhook() 
        logger.info("Webhook and Session deleted successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Обработчик для корневого маршрута "/"
async def root_handler(request):
    try:
        return web.FileResponse('templates/index.html')  # Отдаем файл из папки "templates"
    except FileNotFoundError:
        logger.error("Template file not found")
        return web.Response(status=404, text="Template not found")
    except Exception as e:
        logger.error(f"Error serving root handler: {e}")
        return web.Response(status=500, text="Internal server error")

# Setting up aiohttp application
app = web.Application()
app.router.add_get("/", root_handler)



app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# API: Получение баланса
async def get_balance_handler(request):
    telegram_id = request.query.get("telegram_id")
    if not telegram_id:
        return web.json_response({"error": "telegram_id is required"}, status=400)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return web.json_response({"balance": result[0]})
    return web.json_response({"error": "User not found"}, status=404)

app.router.add_get("/api/balance", get_balance_handler)

# API: Игра в слоты
async def play_slots_handler(request):
    data = await request.json()
    telegram_id = data.get("telegram_id")
    bet = data.get("bet")

    if not telegram_id or not bet:
        return web.json_response({"error": "telegram_id and bet are required"}, status=400)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверяем баланс
    cursor.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
    result = cursor.fetchone()
    if not result or result[0] < bet:
        conn.close()
        return web.json_response({"error": "Insufficient balance"}, status=400)

    # Снимаем ставку
    cursor.execute("UPDATE users SET balance = balance - ? WHERE telegram_id = ?", (bet, telegram_id))

    # Генерация слотов
    SYMBOLS = ["🍒", "🍋", "🍊", "🍇", "⭐"]
    slots = [random.choice(SYMBOLS) for _ in range(3)]
    win_amount = 0

    # Логика выигрыша
    if slots[0] == slots[1] == slots[2]:  # Все три совпадают
        win_amount = bet * 10
    elif slots[0] == slots[1] or slots[1] == slots[2] or slots[0] == slots[2]:  # Два совпадают
        win_amount = bet

    # Обновляем баланс
    cursor.execute("UPDATE users SET balance = balance + ? WHERE telegram_id = ?", (win_amount, telegram_id))
    conn.commit()
    conn.close()

    return web.json_response({"slots": slots, "win_amount": win_amount})

app.router.add_post("/api/slots", play_slots_handler)

# Запуск приложения
if __name__ == '__main__':
    try:
        port = int(os.getenv('PORT', 8080))
        web.run_app(
            app,
            host='0.0.0.0',
            port=port,
            access_log=logger
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")