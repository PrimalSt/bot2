import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command

# Получение токена из переменной окружения
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что переменная BOT_TOKEN установлена.")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Создание клавиатуры для навигации с веб-приложением
casino_web_app = WebAppInfo(url="https://bot2-ksjg.onrender.com/webapp")  # Домен для веб-приложения
web_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Перейти в Казино", web_app=casino_web_app)]
    ]
)

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Добро пожаловать в Казино Бот! \n\n"
        "Вы можете играть в игры и проверять свой баланс. Используйте кнопки ниже.",
        reply_markup=web_button
    )

# Обработчик команды /balance
@dp.message(Command("balance"))
async def balance_handler(message: Message):
    await message.answer("Ваш текущий баланс: 100 монет")

# Обработчик команды /help
@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "Используйте команды или кнопки для взаимодействия:\n" 
        "- /start для начала\n" 
        "- /balance для проверки баланса\n" 
        "- /help для получения справки"
    )

async def on_startup(app: web.Application):
    webhook_url = "https://bot2-ksjg.onrender.com/webhook"  # Используем динамическое получение домена
    await bot.set_webhook(webhook_url)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()

# Маршрут для веб-приложения
def webapp_handler(request):
    return web.Response(text="""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <title>Казино Бот</title>
            <style>body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }</style>
        </head>
        <body>
            <h1>Добро пожаловать в Казино!</h1>
            <button onclick="alert('Вы выиграли!')">Сыграть</button>
        </body>
        </html>
    """, content_type='text/html')

# Создание веб-приложения для обработки вебхуков
app = web.Application()
app.router.add_get("/webapp", webapp_handler)
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Используем порт из переменной окружения Render
    web.run_app(app, host="0.0.0.0", port=port)
