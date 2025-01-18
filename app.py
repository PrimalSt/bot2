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
    try:
        await bot.send_message(
            chat_id=message.chat.id,
            text=(
                "Welcome to Casino Bot! 🎰\n\n"
                "You can play games and check your balance. Use the button below."
            ),
            reply_markup=web_button
        )
    except TelegramAPIError as e:
        logger.error(f"Error in start_handler: {e}")
        await bot.send_message(chat_id=message.chat.id, text="Sorry, an error occurred. Please try again later.")

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


# Setup aiohttp application with middleware

#app.router.add_post('/webhook', handle_webhook)  # Добавление маршрута для обработки вебхука

#async def webapp_handler(request):
   # try:
      #  return web.FileResponse('templates/index.html')
  #  except FileNotFoundError:
  #      logger.error("Template file not found")
  #      return web.Response(status=404, text="Template not found")
 #   except Exception as e:
  #      logger.error(f"Error serving webapp: {e}")
  #      return web.Response(status=500, text="Internal server error")
#app.router.add_get("/webapp", webapp_handler)

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
app.router.add_get("/", root_handler)  # Add handler for root route
app.router.add_post('/webhook', handle_webhook)  # Add handler for webhook# Установка обработчиков событий запуска и завершения работы приложения

app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

def error_response(message, status):
    return web.json_response({
        "error": message,
        "status": status
    }, status=status)

#try:
 #   await message.answer("Сообщение")
#except Exception as e:
 #   print(f"Ошибка отправки сообщения: {e}")

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
