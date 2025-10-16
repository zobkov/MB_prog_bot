#!/usr/bin/env python3
"""
Простой скрипт для отправки сообщения пользователю по ID
Использование: python send_message.py <user_id>
"""

import sys
import asyncio
from aiogram import Bot
from config.config import load_config

# Загружаем конфигурацию
config = load_config()

# Захардкоженное сообщение
MESSAGE = "Мы получили твою оплату. \n<b>Ждем тебя на Менеджменте Будущего '25!</b>"

async def send_message_to_user(user_id: int):
    """Отправляет сообщение пользователю по ID"""
    bot = Bot(token=config.bot.token)
    
    try:
        await bot.send_message(chat_id=user_id, text=MESSAGE, parse_mode='HTML')
        print("=" * 50)
        print(f"✅ УСПЕШНО! Сообщение отправлено пользователю {user_id}")
        print(f"📩 Отправленное сообщение: {MESSAGE}")
        print("=" * 50)
    except Exception as e:
        print("=" * 50)
        print(f"❌ ОШИБКА! Не удалось отправить сообщение пользователю {user_id}")
        print(f"🔍 Детали ошибки: {e}")
        print("=" * 50)
    finally:
        await bot.session.close()

def main():
    if len(sys.argv) != 2:
        print("Использование: python send_message.py <user_id>")
        print("Пример: python send_message.py 123456789")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("❌ Ошибка: ID пользователя должен быть числом")
        sys.exit(1)
    
    print(f"📤 Отправляем сообщение пользователю {user_id}...")
    print(f"📝 Текст сообщения: {MESSAGE}")
    print("=" * 50)
    
    # Запрос подтверждения
    confirm = input("Отправить сообщение? (y/n): ").lower().strip()
    if confirm not in ['y', 'yes', 'д', 'да']:
        print("❌ Отправка отменена")
        return
    
    asyncio.run(send_message_to_user(user_id))

if __name__ == "__main__":
    main()