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
import random
from aiogram.types import Update
import datetime
import json

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована.")

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

# Setting up aiohttp application
app = web.Application()

# Обработчик для получения обновлений от Telegram

async def handle_webhook(request):
    try:
        # Получаем JSON-данные из запроса
        json_data = await request.json()
        update = Update(**json_data)

        # Передаём обновление в диспетчер
        await dp.feed_update(bot=bot, update=update)
        return web.Response(status=200)
    except Exception as e:
        logger.error(f"Error in webhook handler: {e}")
        return web.Response(status=500)

# Регистрация маршрута вебхука

app.router.add_post("/webhook", handle_webhook)
app.router.add_get("/webhook", handle_webhook)

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
        logger.info("Webhook and Session deleted successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# Обработчик для корневого маршрута "/"
async def main_page(request):
    return web.FileResponse("./templates/index.html")

async def shop_page(request):
    return web.FileResponse("./templates/shop.html")

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)
app.router.add_static("/static/", "./static")

async def shop_handler(request):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получаем товары из базы
        cursor.execute("SELECT id, name, price, description FROM shop_items")
        items = cursor.fetchall()
        conn.close()

        return web.json_response({"items": [{"id": row[0], "name": row[1], "price": row[2], "description": row[3]} for row in items]})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

app.router.add_post("/shop", shop_handler)
app.router.add_get("/shop", shop_handler)

async def buy_item_handler(request):
    try:
        data = await request.json()
        telegram_id = data.get("telegram_id")
        item_id = data.get("item_id")

        if not telegram_id or not item_id:
            return web.json_response({"error": "telegram_id and item_id are required"}, status=400)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получаем товар
        cursor.execute("SELECT price FROM shop_items WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        if not item:
            conn.close()
            return web.json_response({"error": "Item not found"}, status=404)

        price = item[0]

        # Проверяем баланс
        cursor.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        if not result or result[0] < price:
            conn.close()
            return web.json_response({"error": "Insufficient balance"}, status=400)

        # Списываем монеты
        cursor.execute("UPDATE users SET balance = balance - ? WHERE telegram_id = ?", (price, telegram_id))
        conn.commit()
        conn.close()

        return web.json_response({"status": "success", "message": "Покупка успешна!"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
    
app.router.add_post("/api/shop/buy", buy_item_handler)
app.router.add_get("/api/shop/buy", buy_item_handler)

async def daily_bonus_handler(request):
    try:
        data = await request.json()
        telegram_id = data.get("telegram_id")

        if not telegram_id:
            return web.json_response({"error": "telegram_id is required"}, status=400)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверяем последнюю выдачу бонуса
        cursor.execute("SELECT last_bonus FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return web.json_response({"error": "User not found"}, status=404)

        last_bonus = result[0]
        today = datetime.date.today()
       
        if last_bonus == str(today):
            conn.close()
            return web.json_response({"error": "Вы уже забирали бонус сегодня"}, status=400)

        # Обновляем баланс и дату бонуса
        cursor.execute("UPDATE users SET balance = balance + 100, last_bonus = ? WHERE telegram_id = ?", (today, telegram_id))
        cursor.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
        new_balance = cursor.fetchone()[0]

        conn.commit()
        conn.close()

        return web.json_response({"new_balance": new_balance})

    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

app.router.add_post("/api/daily_bonus", daily_bonus_handler) 
app.router.add_get("/api/daily_bonus", daily_bonus_handler) 

async def leaderboard_handler(request):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получаем топ-10 игроков по балансу
        cursor.execute("SELECT username, balance FROM users ORDER BY balance DESC LIMIT 10")
        leaderboard = cursor.fetchall()
        conn.close()

        return web.json_response({"leaderboard": leaderboard})

    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)
    
app.router.add_get("/api/leaderboard", leaderboard_handler)

# API: Получение баланса
async def get_balance_handler(request):
    try:
        # Извлекаем JSON-данные из POST-запроса
        data = await request.json()
        telegram_id = data.get("telegram_id")

        # Проверяем, что telegram_id передан
        if not telegram_id:
            return web.json_response({"error": "telegram_id is required"}, status=400)

        # Подключение к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Запрос баланса пользователя
        cursor.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        conn.close()

        # Проверяем, найден ли пользователь
        if result:
            balance = result[0]
            return web.json_response({"balance": balance})
        else:
            return web.json_response({"error": "User not found"}, status=404)

    except sqlite3.Error as e:
        return web.json_response({"error": f"Database error: {str(e)}"}, status=500)

    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

app.router.add_get("/api/balance", get_balance_handler)
app.router.add_post("/api/balance", get_balance_handler)

# API: Игра в слоты
async def slots(request):
    try:
        # Получение данных запроса
        data = await request.json()
        telegram_id = data.get("telegram_id")
        bet = data.get("bet")

        if not telegram_id or not bet:
            return web.json_response({"error": "telegram_id and bet are required"}, status=400)

        # Подключение к базе данных
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Проверяем баланс пользователя
        cursor.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
        result = cursor.fetchone()
        if not result:
            conn.close()
            return web.json_response({"error": "User not found"}, status=404)

        balance = result[0]
        if balance < bet:
            conn.close()
            return web.json_response({"error": "Insufficient balance"}, status=400)

        # Снимаем ставку
        cursor.execute("UPDATE users SET balance = balance - ? WHERE telegram_id = ?", (bet, telegram_id))

        # Генерация слотов
        SYMBOLS = ["🍒", "🍋", "🔔", "⭐", "🍉", "🍇", "🥝"]
        reels = [[random.choice(SYMBOLS) for _ in range(5)] for _ in range(3)]  # 3 ряда, 5 барабанов
        win_amount = 0

        # Проверка выигрышей
        if all(reels[0][i] == reels[1][i] == reels[2][i] for i in range(5)):  # Полный горизонтальный выигрыш
            win_amount = bet * 50
        elif any(reels[0][i] == reels[1][i] == reels[2][i] for i in range(5)):  # Линия из 3 символов
            win_amount = bet * 10
        elif "⭐" in reels[1]:  # Звезда в центральной линии
            win_amount = bet * 5

        # Обновляем баланс
        cursor.execute("UPDATE users SET balance = balance + ? WHERE telegram_id = ?", (win_amount, telegram_id))
        cursor.execute("SELECT balance FROM users WHERE telegram_id = ?", (telegram_id,))
        new_balance = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        return web.json_response({
            "reels": reels,
            "win_amount": win_amount,
            "new_balance": new_balance
        })

    except sqlite3.Error as e:
        return web.json_response({"error": f"Database error: {str(e)}"}, status=500)

    except Exception as e:
        return web.json_response({"error": str(e)}, status=500)

@web.middleware
async def cors_middleware(request, handler):
    response = await handler(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

app.middlewares.append(cors_middleware)

app.router.add_post("/api/slots", slots)
app.router.add_get("/api/slots", slots)
app.router.add_post("/", main_page)
app.router.add_post("/shop", shop_page)
app.router.add_get("/", main_page)
app.router.add_get("/shop", shop_page)
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