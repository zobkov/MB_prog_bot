import asyncio
import asyncpg
from config.config import load_config

async def check_users():
    config = load_config()
    
    # Подключение к PostgreSQL
    conn = await asyncpg.connect(
        host=config.db.host,
        port=config.db.port,
        database=config.db.database,
        user=config.db.user,
        password=config.db.password
    )
    
    print("📊 Все пользователи в базе данных:")
    print("-" * 80)
    
    users = await conn.fetch("SELECT * FROM users ORDER BY created_at DESC")
    
    if not users:
        print("🔍 Пользователи не найдены")
    else:
        for user in users:
            print(f"ID: {user['id']}")
            print(f"Telegram ID: {user['telegram_id']}")
            print(f"Username: @{user['username'] or 'не указан'}")
            print(f"Имя: {user['first_name']} {user['last_name']}")
            print(f"Пакет: {user['package_type']}")
            print(f"Участвовал ранее: {user['participated_before']}")
            if user['participated_before']:
                print(f"Год участия: {user['participation_year']}")
            print(f"Выпускник ВШМ: {user['is_vsm_graduate']}")
            if user['graduation_year']:
                print(f"Год выпуска: {user['graduation_year']}")
            print(f"Создан: {user['created_at']}")
            print(f"Обновлен: {user['updated_at']}")
            print("-" * 80)
    
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_users())
