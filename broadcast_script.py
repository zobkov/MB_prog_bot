"""
Скрипт для рассылки сообщений участникам из CSV файла

Особенности:
- Поддержка dry-run режима
- Обязательное подтверждение перед отправкой
- Чтение данных из CSV файла
- Формирование персонализированных сообщений
- Отправка через основной бот с обработчиками
"""

import asyncio
import csv
import logging
from typing import List, Dict, Any
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from config.config import load_config


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BroadcastScript:
    def __init__(self, csv_file_path: str = "broadcast.csv"):
        self.csv_file_path = csv_file_path
        self.config = load_config()
        self.bot = None
        
        # Маппинг пакетов
        self.package_mapping = {
            1: "Деловая программа – 2 990 руб.",
            2: "Гала-ужин – 3 490 руб.",
            3: "Деловая программа & гала-ужин – 5 990 руб."
        }
        
        # Дополнительная информация для пакетов
        self.package_additional_info = {
            1: "\n❗ Мы также предлагаем приобрести полный пакет участия за 6 490 рублей. Так ты сможешь посетить не только деловую программу 3-го дня, но и гала-ужин, который завершает конференцию.",
            2: "\n❗ Мы также предлагаем приобрести полный пакет участия за 6 490 рублей. Так ты сможешь посетить не только гала-ужин, но и деловую программу 3-го дня.",
            3: ""  # Для полного пакета дополнительной информации нет
        }
        
        # Базовый текст сообщения
        self.message_template = """Всем привет! 

✨Мы готовы объявить о запуске продаж билетов на деловую программу и гала ужин. 

Выбранный пакет участия: {package_name}{package_additional_info}


Для оплаты переведи сумму согласно выбранному тарифу по номеру телефона +7 (960) 259 88-47 на Альфа-банк (Дмитрий К.). 

В течении 24 часов после оплаты в боте придет подтверждение. Убедительная просьба: не отключай уведомления!

Ждем тебя на Менеджменте Будущего '25!"""

        # Текст для кнопки "Что в программе?"
        self.program_info_text = """<b>Третий день МБ: буст личностного развития</b>

Этот трек мы посвящаем вам — выпускникам, что строят будущее в менеджменте. Программа насыщена практикой и нетворкингом, чтобы дать вам максимум полезного для карьеры.

🎯 <b>Деловая программа:</b>

<b>12:00–13:20 | Игра-интерактив по коммуникации в команде</b>
Разберём реальные сложности общения в корпоративной среде в лёгком игровом формате. Вы откроете для себя конкретные инструменты, которые помогают понимать коллег и достигать общих целей без лишнего стресса. Погрузимся в живые кейсы и найдём решения для типичных рабочих конфликтов.

<b>14:30–15:10 | Воркшоп по самопрезентации</b>
Научимся рассказывать о себе так, чтобы вас запоминали — и как профессионала, и как интересную личность. Вы освоите 3 подхода и создадите 3 варианта самопрезентации для ключевых ситуаций: собеседование, карьерное мероприятие, неформальное знакомство. Узнаете, как подчеркнуть свои сильные стороны и уверенно держаться перед любой аудиторией.

<b>15:10–15:30 | Нетворкинг в формате быстрых встреч</b>
Динамичный формат с короткими переходами от стола к столу, обменом мнений по карточкам и свободными диалогами. Это отличный и быстрый способ расширить круг полезных знакомств и найти единомышленников в индустрии.

👩‍🏫 <b>Спикеры и фасилитаторы:</b>

Катя Митусова — Лидер Women in Tech Russia, ex-Google, ex-Wrike, Platinum Tier Facilitator #IamRemarkable

Оля Чадулина — HR в IT, ex-Raiffeisenbank, карьерный ментор и коуч ICF, автор канала «Всё ты можешь»

Лена Соколова — Product Owner в EdTech, ex-Нетология, ex-Яндекс Практикум, автор канала и подкаста «Карьера без багов», сооснователь сообщества «Ещё не продакты»

✨ <b>Почему стоит быть?</b>

Финальный день — это ваша возможность прокачать ключевые навыки, получить свежие инсайты и пообщаться с теми, кто разделяет ваш интерес к будущему в менеджменте.

<b>Ждём именно вас, выпускников Конференции и Высшей Школы Менеджмента!</b>"""

    async def initialize_bot(self):
        """Инициализация бота"""
        self.bot = Bot(
            token=self.config.bot.token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

    async def close_bot(self):
        """Закрытие сессии бота"""
        if self.bot:
            await self.bot.session.close()

    def read_csv_data(self) -> List[Dict[str, Any]]:
        """Чтение данных из CSV файла"""
        users = []
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Исправляем опечатку в названии колонки (pacakage -> package)
                    if 'pacakage' in row:
                        row['package'] = row['pacakage']
                    
                    users.append({
                        'id': int(row['id']),
                        'telegram_id': int(row['telegram_id']),
                        'username': row.get('username', ''),
                        'package': int(row['package'])
                    })
        except FileNotFoundError:
            logger.error(f"CSV файл {self.csv_file_path} не найден")
            return []
        except Exception as e:
            logger.error(f"Ошибка при чтении CSV файла: {e}")
            return []
        
        return users

    def create_keyboard(self) -> InlineKeyboardMarkup:
        """Создание клавиатуры с кнопками"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Что в программе?", callback_data="program_info")],
            [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data="confirm_payment")],
            [InlineKeyboardButton(text="❌ Отказаться от участия", callback_data="decline_participation")]
        ])
        return keyboard

    def format_message(self, package_id: int) -> str:
        """Формирование персонализированного сообщения"""
        package_name = self.package_mapping.get(package_id, "Неизвестный пакет")
        package_additional_info = self.package_additional_info.get(package_id, "")
        
        return self.message_template.format(
            package_name=package_name,
            package_additional_info=package_additional_info
        )

    def display_preview(self, users: List[Dict[str, Any]]):
        """Показ превью рассылки"""
        print("\n" + "="*80)
        print("ПРЕВЬЮ РАССЫЛКИ")
        print("="*80)
        print(f"Общее количество получателей: {len(users)}")
        print()
        
        # Группировка по пакетам
        package_stats = {}
        for user in users:
            package = user['package']
            if package not in package_stats:
                package_stats[package] = 0
            package_stats[package] += 1
        
        print("Статистика по пакетам:")
        for package_id, count in package_stats.items():
            package_name = self.package_mapping.get(package_id, f"Неизвестный пакет {package_id}")
            print(f"  {package_name}: {count} получателей")
        
        print("\nПример сообщения для каждого типа пакета:")
        print("-" * 80)
        
        for package_id in sorted(package_stats.keys()):
            print(f"\nПАКЕТ {package_id}: {self.package_mapping.get(package_id, 'Неизвестный')}")
            print("-" * 50)
            print(self.format_message(package_id))
            print()

    async def send_message_to_user(self, user: Dict[str, Any], dry_run: bool = True) -> bool:
        """Отправка сообщения одному пользователю"""
        try:
            message_text = self.format_message(user['package'])
            keyboard = self.create_keyboard()
            
            if dry_run:
                print(f"[DRY RUN] Отправка сообщения пользователю {user['telegram_id']} (@{user['username']})")
                return True
            else:
                await self.bot.send_message(
                    chat_id=user['telegram_id'],
                    text=message_text,
                    reply_markup=keyboard
                )
                logger.info(f"Сообщение отправлено пользователю {user['telegram_id']} (@{user['username']})")
                return True
                
        except TelegramForbiddenError:
            logger.warning(f"Пользователь {user['telegram_id']} заблокировал бота")
            return False
        except TelegramBadRequest as e:
            logger.error(f"Ошибка отправки пользователю {user['telegram_id']}: {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при отправке пользователю {user['telegram_id']}: {e}")
            return False

    async def run_broadcast(self, dry_run: bool = True):
        """Запуск рассылки"""
        print("🤖 Запуск скрипта рассылки...")
        
        # Чтение данных из CSV
        users = self.read_csv_data()
        if not users:
            print("❌ Нет данных для рассылки. Проверьте CSV файл.")
            return
        
        # Показ превью
        self.display_preview(users)
        
        if dry_run:
            print("\n🔍 РЕЖИМ DRY RUN - сообщения НЕ будут отправлены")
            print("Для настоящей отправки запустите с параметром --send")
        else:
            print("\n⚠️  ВНИМАНИЕ! Это НАСТОЯЩАЯ РАССЫЛКА!")
            print("Сообщения будут отправлены всем пользователям из списка.")
            
            confirmation = input("\nВы уверены, что хотите продолжить? (введите 'ДА' для подтверждения): ")
            if confirmation.upper() != 'ДА':
                print("❌ Рассылка отменена.")
                return
            
            # Инициализация бота
            await self.initialize_bot()
        
        # Отправка сообщений
        successful_sends = 0
        failed_sends = 0
        
        print(f"\n📤 Начинаем {'симуляцию' if dry_run else 'отправку'} сообщений...")
        
        for i, user in enumerate(users, 1):
            print(f"[{i}/{len(users)}] Обработка пользователя {user['telegram_id']}...")
            
            success = await self.send_message_to_user(user, dry_run)
            
            if success:
                successful_sends += 1
            else:
                failed_sends += 1
            
            # Пауза между отправками (только для реальной отправки)
            if not dry_run:
                await asyncio.sleep(0.1)  # 100ms пауза между сообщениями
        
        # Итоговая статистика
        print("\n" + "="*80)
        print("ИТОГИ РАССЫЛКИ" if not dry_run else "ИТОГИ СИМУЛЯЦИИ")
        print("="*80)
        print(f"✅ Успешно {'отправлено' if not dry_run else 'обработано'}: {successful_sends}")
        print(f"❌ Ошибок: {failed_sends}")
        print(f"📊 Общий процент успеха: {(successful_sends / len(users) * 100):.1f}%")
        
        if not dry_run:
            await self.close_bot()


async def main():
    """Главная функция скрипта"""
    import sys
    import argparse
    
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Скрипт рассылки сообщений')
    parser.add_argument('--send', action='store_true', help='Реальная отправка (по умолчанию dry-run)')
    parser.add_argument('--csv', type=str, default='broadcast.csv', help='Путь к CSV файлу (по умолчанию broadcast.csv)')
    
    args = parser.parse_args()
    
    # Создание и запуск скрипта рассылки
    broadcast = BroadcastScript(csv_file_path=args.csv)
    await broadcast.run_broadcast(dry_run=not args.send)


if __name__ == "__main__":
    asyncio.run(main())