from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram_dialog import DialogManager, StartMode
from bot.states import RegistrationSG

router = Router()

# ID администратора для уведомлений
ADMIN_ID = 257026813


@router.message(CommandStart())
async def start_command(message: Message, dialog_manager: DialogManager):
    """Обработчик команды /start"""
    await dialog_manager.start(RegistrationSG.welcome, mode=StartMode.RESET_STACK)


@router.message(Command(commands=['menu']))
async def process_command_menu(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=RegistrationSG.welcome, mode=StartMode.RESET_STACK)


@router.message(Command(commands=['stats']))
async def process_command_stats(message: Message):
    """Обработчик команды /stats - только для администратора"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этой команде.")
        return
    
    # Здесь можно добавить логику получения статистики из базы данных
    stats_text = """📊 <b>СТАТИСТИКА МБ'25</b>

🔍 <b>Активность по кнопкам:</b>
• Запросы программы: - (функция в разработке)
• Подтверждения оплаты: - (функция в разработке)  
• Отказы от участия: - (функция в разработке)

📝 <b>Общая статистика:</b>
• Всего пользователей: - (функция в разработке)
• Активных участников: - (функция в разработке)

💡 Для получения детальной статистики добавьте интеграцию с базой данных."""
    
    await message.answer(stats_text)


# Обработчики для кнопок рассылки

@router.callback_query(F.data == "program_info")
async def handle_program_info(callback: CallbackQuery):
    """Обработчик кнопки 'Что в программе?'"""
    program_text = """<b>Третий день МБ: буст личностного развития</b>

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
    
    await callback.message.answer(program_text)
    await callback.answer()


@router.callback_query(F.data == "confirm_payment")
async def handle_confirm_payment(callback: CallbackQuery, user_repo):
    """Обработчик кнопки 'Подтвердить оплату'"""
    user_id = callback.from_user.id
    username = callback.from_user.username or "без username"
    full_name = callback.from_user.full_name or "Неизвестно"
    
    # Здесь можно добавить логику сохранения подтверждения в базу данных
    # Например: await user_repo.set_payment_confirmed(user_id, True)
    
    # Новый текст для замены оригинального сообщения
    confirm_text = """✅ <b>Подтверждение оплаты получено!</b>

Спасибо за подтверждение!

В течение 24 часов наша команда проверит платеж и вышлет подтверждение участия.

Если у вас есть вопросы, не стесняйтесь обращаться к нам.

<b>До встречи на Менеджменте Будущего '25!</b> 🎉"""
    
    # Уведомление администратору о подтверждении оплаты
    admin_notification = f"""💰 <b>ПОДТВЕРЖДЕНИЕ ОПЛАТЫ</b>

👤 <b>Пользователь:</b> {full_name}
🆔 <b>ID:</b> <code>{user_id}</code>
📧 <b>Username:</b> @{username}
📅 <b>Время:</b> {callback.message.date.strftime('%d.%m.%Y %H:%M')}

✅ Пользователь подтвердил оплату участия в МБ'25"""
    
    # Удаляем оригинальное сообщение и отправляем новое
    await callback.message.delete()
    await callback.message.answer(confirm_text)
    
    # Отправка уведомления администратору
    try:
        await callback.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_notification
        )
    except Exception as e:
        # Логируем ошибку, но не прерываем основной процесс
        import logging
        logging.error(f"Ошибка отправки уведомления админу: {e}")
    
    await callback.answer("Подтверждение получено!")


@router.callback_query(F.data == "decline_participation")
async def handle_decline_participation(callback: CallbackQuery, user_repo):
    """Обработчик кнопки 'Отказаться от участия'"""
    user_id = callback.from_user.id
    username = callback.from_user.username or "без username"
    full_name = callback.from_user.full_name or "Неизвестно"
    
    # Здесь можно добавить логику сохранения отказа в базу данных
    # Например: await user_repo.set_participation_declined(user_id, True)
    
    # Новый текст для замены оригинального сообщения
    decline_text = """❌ <b>Отказ от участия</b>

Вы отказались от участия.

Мы понимаем, что планы могут меняться. Если передумаете, всегда можете написать нам."""
    
    # Уведомление администратору об отказе от участия
    admin_notification = f"""❌ <b>ОТКАЗ ОТ УЧАСТИЯ</b>

👤 <b>Пользователь:</b> {full_name}
🆔 <b>ID:</b> <code>{user_id}</code>
📧 <b>Username:</b> @{username}
📅 <b>Время:</b> {callback.message.date.strftime('%d.%m.%Y %H:%M')}

💔 Пользователь отказался от участия в МБ'25"""
    
    # Удаляем оригинальное сообщение и отправляем новое
    await callback.message.delete()
    await callback.message.answer(decline_text)
    
    # Отправка уведомления администратору
    try:
        await callback.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_notification
        )
    except Exception as e:
        # Логируем ошибку, но не прерываем основной процесс
        import logging
        logging.error(f"Ошибка отправки уведомления админу: {e}")
    
    await callback.answer("Мы учли ваше решение")