#!/usr/bin/env python3
"""
Утилита для управления данными бота MB25
"""
import asyncio
import sys
from config.config import load_config
from bot.database import Database, UserRepository
from sqlalchemy import select, func


async def show_all_users():
    """Показать всех зарегистрированных пользователей"""
    config = load_config()
    database = Database(config)
    user_repo = UserRepository(database)
    
    try:
        # Получаем всех пользователей
        session = await database.get_session()
        try:
            from bot.models import User
            result = await session.execute(select(User).order_by(User.created_at.desc()))
            users = result.scalars().all()
            
            if not users:
                print("📝 Пользователи не найдены")
                return
            
            print(f"📊 Всего зарегистрированных пользователей: {len(users)}")
            print("=" * 80)
            
            for user in users:
                print(f"👤 ID: {user.id}")
                print(f"   Telegram ID: {user.telegram_id}")
                username_display = f"@{user.username}" if user.username else "Нет username"
                print(f"   Username: {username_display}")
                print(f"   Имя: {user.first_name} {user.last_name}")
                print(f"   Пакет: {user.package_type}")
                print(f"   Участвовал в МБ ранее: {'Да' if user.participated_before else 'Нет'}")
                if user.participated_before and user.participation_year:
                    print(f"   Год участия: {user.participation_year}")
                print(f"   Выпускник ВШМ: {'Да' if user.is_vsm_graduate else 'Нет'}")
                if user.is_vsm_graduate and user.graduation_year:
                    print(f"   Год выпуска: {user.graduation_year}")
                print(f"   Дата регистрации: {user.created_at}")
                print("-" * 40)
        finally:
            await session.close()
            
    except Exception as e:
        print(f"❌ Ошибка при получении пользователей: {e}")
    finally:
        await database.close()


async def show_statistics():
    """Показать статистику регистраций"""
    config = load_config()
    database = Database(config)
    
    try:
        session = await database.get_session()
        try:
            from bot.models import User
            
            # Общая статистика
            total_users = await session.execute(select(func.count(User.id)))
            total_count = total_users.scalar()
            
            # Статистика по пакетам
            business_count_result = await session.execute(
                select(func.count(User.id)).where(User.package_type == 'business')
            )
            business_count = business_count_result.scalar()
            
            gala_count_result = await session.execute(
                select(func.count(User.id)).where(User.package_type == 'gala')
            )
            gala_count = gala_count_result.scalar()
            
            full_count_result = await session.execute(
                select(func.count(User.id)).where(User.package_type == 'full')
            )
            full_count = full_count_result.scalar()
            
            # Статистика по участию в МБ
            participated_before_result = await session.execute(
                select(func.count(User.id)).where(User.participated_before == True)
            )
            participated_before_count = participated_before_result.scalar()
            
            # Статистика по выпускникам ВШМ
            vsm_graduates_result = await session.execute(
                select(func.count(User.id)).where(User.is_vsm_graduate == True)
            )
            vsm_graduates_count = vsm_graduates_result.scalar()
            
            print("📊 СТАТИСТИКА РЕГИСТРАЦИЙ")
            print("=" * 50)
            print(f"Всего пользователей: {total_count}")
            print("\n📦 По пакетам:")
            print(f"  • Деловая программа: {business_count}")
            print(f"  • Гала-ужин: {gala_count}")
            print(f"  • Полный пакет: {full_count}")
            print(f"\n🎓 Участвовали в МБ ранее: {participated_before_count}")
            print(f"🏫 Выпускники ВШМ: {vsm_graduates_count}")
            
        finally:
            await session.close()
            
    except Exception as e:
        print(f"❌ Ошибка при получении статистики: {e}")
    finally:
        await database.close()


async def clear_all_users():
    """Очистить всех пользователей (для тестирования)"""
    config = load_config()
    database = Database(config)
    
    print("⚠️  ВНИМАНИЕ: Это удалит ВСЕХ пользователей из базы данных!")
    confirm = input("Введите 'YES' для подтверждения: ")
    
    if confirm != 'YES':
        print("❌ Операция отменена")
        return
    
    try:
        session = await database.get_session()
        try:
            from bot.models import User
            await session.execute(User.__table__.delete())
            await session.commit()
            print("✅ Все пользователи успешно удалены")
        finally:
            await session.close()
            
    except Exception as e:
        print(f"❌ Ошибка при удалении пользователей: {e}")
    finally:
        await database.close()


def print_help():
    """Показать справку по командам"""
    print("🤖 MB25 Bot Data Manager")
    print("=" * 30)
    print("Доступные команды:")
    print("  users     - Показать всех пользователей")
    print("  stats     - Показать статистику")
    print("  clear     - Очистить всех пользователей")
    print("  help      - Показать эту справку")


async def main():
    if len(sys.argv) < 2:
        print_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'users':
        await show_all_users()
    elif command == 'stats':
        await show_statistics()
    elif command == 'clear':
        await clear_all_users()
    elif command == 'help':
        print_help()
    else:
        print(f"❌ Неизвестная команда: {command}")
        print_help()


if __name__ == "__main__":
    asyncio.run(main())