import os
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiohttp import web
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command

# Получение токена из переменной окружения
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    raise ValueError("Токен бота не найден. Убедитесь, что переменная BOT_TOKEN установлена.")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN, session=AiohttpSession())
dp = Dispatcher(bot=bot, storage=MemoryStorage())

# Создание клавиатуры для навигации с веб-приложением
casino_web_app = WebAppInfo(url="https://bot2-ksjg.onrender.com/webapp")
web_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Перейти в Казино", web_app=casino_web_app)]
    ]
)

# Обработчик команды /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        "Добро пожаловать в Казино Бот! \n\n"
        "Вы можете играть в игры и проверять свой баланс. Используйте кнопку ниже.",
        reply_markup=web_button
    )

# Обработчик для получения обновлений от Telegram
async def handle_webhook(request):
    json_data = await request.json()
    update = types.Update(**json_data)

    # Проверяем тип обновления и вызываем соответствующий обработчик.
    if update.message and update.message.text:
        message = update.message
        if message.text == "/start":
            await start_handler(message)
    
    return web.Response(status=200)

async def on_startup(app: web.Application):
    webhook_url = "https://bot2-ksjg.onrender.com/webhook"  # Убедитесь, что этот URL доступен
    await bot.set_webhook(webhook_url)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()  # Удаляем вебхук

# Настройка приложения aiohttp
app = web.Application()
app.router.add_post('/webhook', handle_webhook)  # Добавление маршрута для обработки вебхука

# Установка обработчиков событий запуска и завершения работы приложения
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# Запуск приложения
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=int(os.getenv('PORT', 8080)))  # Порт можно задать через переменные окружения или использовать 8080 по умолчанию.
