#!/usr/bin/env python3
"""
Простая миграция для добавления поля username в таблицу users
"""
import asyncio
from config.config import load_config
from bot.database import Database


async def add_username_column():
    """Добавляет колонку username в таблицу users"""
    config = load_config()
    database = Database(config)
    
    try:
        session = await database.get_session()
        try:
            # SQL для добавления колонки
            from sqlalchemy import text
            sql = text("ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(100);")
            await session.execute(sql)
            await session.commit()
            print("✅ Колонка username успешно добавлена в таблицу users")
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при добавлении колонки: {e}")
        finally:
            await session.close()
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
    finally:
        await database.close()


if __name__ == "__main__":
    print("🔄 Выполнение миграции: добавление поля username...")
    asyncio.run(add_username_column())