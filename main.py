import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from redis.asyncio import Redis

from config.config import load_config
from bot.handlers import router
from bot.dialogs import registration_dialog
from bot.database import Database, UserRepository
from bot.google_sheets import GoogleSheetsService
from bot.google_sheets_middleware import GoogleSheetsMiddleware
from bot.media_manager import MediaManager


async def main():
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Загрузка конфигурации
    config = load_config()
    
    # Создание Redis клиента для FSM
    if config.redis.password:
        redis_client = Redis.from_url(f"redis://:{config.redis.password}@{config.redis.host}:{config.redis.port}/0")
    else:
        redis_client = Redis.from_url(f"redis://{config.redis.host}:{config.redis.port}/0")
    
    # Проверка подключения к Redis
    try:
        await redis_client.ping()
        print(f"✅ Подключение к Redis установлено: {config.redis.host}:{config.redis.port}")
    except Exception as e:
        print(f"❌ Ошибка подключения к Redis: {e}")
        return
    
    # Создание хранилища для FSM
    storage = RedisStorage(
        redis=redis_client,
        key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True)
    )
    
    # Создание бота и диспетчера
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)
    
    # Создание и настройка базы данных
    database = Database(config)
    await database.create_tables()
    user_repo = UserRepository(database)
    
    # Создание Google Sheets сервиса
    google_sheets_service = None
    try:
        if config.google_sheets.spreadsheet_url and config.google_sheets.credentials_path:
            google_sheets_service = GoogleSheetsService(
                config.google_sheets.credentials_path,
                config.google_sheets.spreadsheet_url
            )
            print("✅ Google Sheets сервис инициализирован")
        else:
            print("⚠️ Конфигурация Google Sheets не найдена")
    except Exception as e:
        print(f"⚠️ Ошибка инициализации Google Sheets: {e}")
    
    # Создание MediaManager
    media_manager = MediaManager(bot)
    
    # Middleware для передачи database, user_repo, google_sheets и media_manager
    async def services_middleware(handler, event, data):
        data["database"] = database
        data["user_repo"] = user_repo
        data["google_sheets"] = google_sheets_service
        data["media_manager"] = media_manager
        return await handler(event, data)
    
    # Регистрация middleware
    dp.message.middleware(services_middleware)
    dp.callback_query.middleware(services_middleware)
    
    # Регистрация роутеров и диалогов
    dp.include_router(router)
    dp.include_router(registration_dialog)
    
    # Настройка aiogram-dialog
    setup_dialogs(dp)
    
    print("🤖 Бот запущен и готов к работе!")
    
    # Запуск бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await database.close()
        await redis_client.aclose()


if __name__ == '__main__':
    asyncio.run(main())