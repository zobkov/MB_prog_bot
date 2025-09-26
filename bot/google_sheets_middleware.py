from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from bot.google_sheets import GoogleSheetsService

class GoogleSheetsMiddleware(BaseMiddleware):
    """Middleware для передачи Google Sheets сервиса в обработчики"""
    
    def __init__(self, google_sheets_service: GoogleSheetsService):
        self.google_sheets_service = google_sheets_service
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data["google_sheets"] = self.google_sheets_service
        return await handler(event, data)