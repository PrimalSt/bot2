import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Получение токена из переменной окружения
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что переменная BOT_TOKEN установлена.")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Создание клавиатуры для навигации
navigation_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Играть"), KeyboardButton(text="Баланс")],
        [KeyboardButton(text="Пополнить баланс"), KeyboardButton(text="Помощь")]
    ],
    resize_keyboard=True
)

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "Добро пожаловать в Казино Бот! \n\n"
        "Вы можете играть в игры и проверять свой баланс. Используйте кнопки ниже.",
        reply_markup=navigation_keyboard
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
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/webhook"  # Используем динамическое получение домена
    await bot.set_webhook(webhook_url)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()

# Создание веб-приложения для обработки вебхуков
app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))  # Используем порт из переменной окружения Render
    web.run_app(app, host="0.0.0.0", port=port)