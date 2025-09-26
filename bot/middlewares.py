from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from bot.database import Database, UserRepository


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, database: Database):
        self.database = database
        self.user_repo = UserRepository(database)
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        data['database'] = self.database
        data['user_repo'] = self.user_repo
        return await handler(event, data)