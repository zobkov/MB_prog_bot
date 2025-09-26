import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import select
from config.config import load_config, Config
from bot.models import Base, User


class Database:
    def __init__(self, config: Config):
        self.config = config
        db_url = f"postgresql+psycopg://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.database}"
        
        self.engine = create_async_engine(
            db_url,
            poolclass=NullPool,
            echo=True
        )
        
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Создание всех таблиц"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def get_session(self) -> AsyncSession:
        """Получение сессии для работы с БД"""
        return self.async_session()
    
    async def close(self):
        """Закрытие соединения с БД"""
        await self.engine.dispose()


# Функции для работы с пользователями
class UserRepository:
    def __init__(self, db: Database):
        self.db = db
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> User:
        """Получение пользователя по telegram_id"""
        session = await self.db.get_session()
        try:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            return result.scalar_one_or_none()
        finally:
            await session.close()
    
    async def create_user(self, user_data: dict) -> User:
        """Создание нового пользователя или обновление существующего"""
        session = await self.db.get_session()
        try:
            # Сначала проверяем, существует ли пользователь
            existing_user_result = await session.execute(
                select(User).where(User.telegram_id == user_data["telegram_id"])
            )
            existing_user = existing_user_result.scalar_one_or_none()
            
            if existing_user:
                # Обновляем существующего пользователя
                for key, value in user_data.items():
                    if key != "telegram_id":  # telegram_id не меняем
                        setattr(existing_user, key, value)
                await session.commit()
                await session.refresh(existing_user)
                return existing_user
            else:
                # Создаем нового пользователя
                user = User(**user_data)
                session.add(user)
                await session.commit()
                await session.refresh(user)
                return user
        finally:
            await session.close()
    
    async def update_user(self, telegram_id: int, user_data: dict) -> User:
        """Обновление данных пользователя"""
        session = await self.db.get_session()
        try:
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalar_one_or_none()
            if user:
                for key, value in user_data.items():
                    setattr(user, key, value)
                await session.commit()
                await session.refresh(user)
            return user
        finally:
            await session.close()