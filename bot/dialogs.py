from typing import Any, Dict
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window, ShowMode
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, Column, Select
from aiogram_dialog.widgets.input import TextInput
from bot.states import RegistrationSG


# Тексты для бота
WELCOME_TEXT = """Дорогие выпускники! 

В этом году на МБ25 мы хотим предоставить вам возможность снова стать частью конференции! Для этого мы придумали специальную программу для выпускников. Вы сможете посетить деловую программу третьего дня, послушать выступления и дискуссии уважаемых спикеров, а также принять участие в нетворкинге - развить свои софтскиллы и приобрести ценные деловые контакты."""

PACKAGES_TEXT = """Мы предлагаем посетить конференцию в третий день - 25 октября. Есть три варианта участия:

1. Деловая программа - участие в мероприятиях третьего дня конференции (25 октября). 
Вас ждут интересные лекции от топовых спикеров, панельные дискуссии на актуальные темы, а также интерактивное мероприятие для выпускников с перерывом на нетворкинг. Вы сможете отработать навык целеполагания и деловой коммуникации и получить массу новых знакомств. Сплошная польза с утра и до самого вечера.
Стоимость: 2 990р

2. Гала-ужин - закрытие конференции в ресторане с панорамным видом на Петербург.
Ваш шанс за бокалом игристого пообщаться с нынешними участниками конференции - насладиться приятной компанией и вкусным фуршетом. 
Стоимость: 3 490р

3. Деловая программа и гала-ужин - целый день интересных мероприятий и прекрасный праздник вечером.
Сначала послушаете все самые крутые мероприятия третьего дня, а вечером отдохнете на ужине в ресторане с видом на ночной город.
Стоимость: 5 990р

Чтобы попасть в лист ожидания, выбери пакет участия, который тебе наиболее интересен."""

COMPLETION_TEXT = """Спасибо, что зарегистрировался! В этот бот придет уведомление, когда откроются продажи. Не пропусти!"""

PROGRAM_TEXT = """<b>3-й день: Личностное развитие</b>

Завершающий день конференции посвящен развитию креативности и личной эффективности. Спикеры раскроют секреты становления успешным специалистом и определят ключевые софт скиллы, необходимые в современной карьере. В программе — интерактивные дискуссии о роли творческого мышления в бизнесе и нетворкинг-сессии для создания профессиональных связей.

Подробная программа дня появится позже. Жди уведомлений в боте!"""


# Геттеры данных для диалогов
async def get_packages_data(**kwargs):
    return {
        "packages": [
            ("Деловая программа - 2 990", "business"),
            ("Гала-ужин - 3 490", "gala"),
            ("Деловая программа и гала-ужин - 5 990", "full"),
        ]
    }


# Обработчики кнопок и ввода
async def on_package_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data["package_type"] = item_id
    await dialog_manager.switch_to(RegistrationSG.first_name, show_mode=ShowMode.SEND)


async def on_first_name_input(message: Message, widget, dialog_manager: DialogManager, text: str):
    if len(text.strip()) < 2:
        await message.answer("Имя должно содержать минимум 2 символа. Попробуйте еще раз.")
        return
    dialog_manager.dialog_data["first_name"] = text.strip()
    await dialog_manager.next()


async def on_last_name_input(message: Message, widget, dialog_manager: DialogManager, text: str):
    if len(text.strip()) < 2:
        await message.answer("Фамилия должна содержать минимум 2 символа. Попробуйте еще раз.")
        return
    dialog_manager.dialog_data["last_name"] = text.strip()
    await dialog_manager.next()


async def on_participated_yes(callback: CallbackQuery, widget, dialog_manager: DialogManager):
    dialog_manager.dialog_data["participated_before"] = True
    await dialog_manager.next()


async def on_participated_no(callback: CallbackQuery, widget, dialog_manager: DialogManager):
    dialog_manager.dialog_data["participated_before"] = False
    dialog_manager.dialog_data["participation_year"] = None
    await dialog_manager.switch_to(RegistrationSG.is_vsm_graduate)


async def on_participation_year_input(message: Message, widget, dialog_manager: DialogManager, text: str):
    year = text.strip()
    if not year.isdigit() or len(year) != 4 or int(year) < 2000 or int(year) > 2024:
        await message.answer("Введите корректный год участия (например, 2023).")
        return
    dialog_manager.dialog_data["participation_year"] = year
    await dialog_manager.next()


async def on_vsm_graduate_yes(callback: CallbackQuery, widget, dialog_manager: DialogManager):
    dialog_manager.dialog_data["is_vsm_graduate"] = True
    await dialog_manager.next()


async def on_vsm_graduate_no(callback: CallbackQuery, widget, dialog_manager: DialogManager):
    dialog_manager.dialog_data["is_vsm_graduate"] = False
    dialog_manager.dialog_data["graduation_year"] = None
    await complete_registration(callback, widget, dialog_manager)


async def on_graduation_year_input(message: Message, widget, dialog_manager: DialogManager, text: str):
    year = text.strip()
    if not year.isdigit() or len(year) != 4 or int(year) < 1990 or int(year) >= 2026:
        await message.answer("Введите корректный год выпуска (например, 2020).")
        return
    dialog_manager.dialog_data["graduation_year"] = year
    await complete_registration(None, widget, dialog_manager)


async def complete_registration(callback, widget, dialog_manager: DialogManager):
    # Сохранение данных в БД
    user_data = {
        "telegram_id": dialog_manager.event.from_user.id,
        "username": dialog_manager.event.from_user.username,  # Telegram username
        "first_name": dialog_manager.dialog_data["first_name"],
        "last_name": dialog_manager.dialog_data["last_name"],
        "package_type": dialog_manager.dialog_data["package_type"],
        "participated_before": dialog_manager.dialog_data["participated_before"],
        "participation_year": dialog_manager.dialog_data.get("participation_year"),
        "is_vsm_graduate": dialog_manager.dialog_data["is_vsm_graduate"],
        "graduation_year": dialog_manager.dialog_data.get("graduation_year"),
    }
    
    saved_user = None
    
    # Сохранение в БД
    try:
        user_repo = dialog_manager.middleware_data.get('user_repo')
        if user_repo:
            saved_user = await user_repo.create_user(user_data)
            print(f"✅ Пользователь {user_data['telegram_id']} успешно сохранен в БД")
        else:
            print("⚠️ UserRepository не найден в middleware_data")
    except Exception as e:
        # Логируем ошибку, но продолжаем работу
        print(f"❌ Ошибка сохранения пользователя: {e}")
    
    # Сохранение в Google Sheets
    if saved_user:
        try:
            google_sheets = dialog_manager.middleware_data.get('google_sheets')
            if google_sheets:
                success = google_sheets.add_user_to_sheet(saved_user)
                if success:
                    print(f"✅ Пользователь {user_data['telegram_id']} успешно добавлен в Google Sheets")
                else:
                    print(f"⚠️ Не удалось добавить пользователя в Google Sheets")
            else:
                print("⚠️ Google Sheets сервис не найден в middleware_data")
        except Exception as e:
            print(f"❌ Ошибка записи в Google Sheets: {e}")
    
    await dialog_manager.switch_to(RegistrationSG.completed)


# Определение диалога
registration_dialog = Dialog(
    # Окно приветствия
    Window(
        Const(WELCOME_TEXT),
        Column(
            Button(
                Const("Как можно поучаствовать?"),
                id="how_to_participate",
                on_click=lambda c, w, m: m.switch_to(RegistrationSG.package_selection)
            ),
            Button(
                Const("А что в программе?"),
                id="show_program",
                on_click=lambda c, w, m: m.switch_to(RegistrationSG.program_info)
            ),
        ),
        state=RegistrationSG.welcome,
    ),
    
    # Окно программы дня
    Window(
        Const(PROGRAM_TEXT),
        Button(
            Const("◀️ Назад"),
            id="back_to_welcome",
            on_click=lambda c, w, m: m.switch_to(RegistrationSG.welcome)
        ),
        state=RegistrationSG.program_info,
    ),
    
    # Окно выбора пакетов
    Window(
        Const(PACKAGES_TEXT),
        Column(
            Select(
                Format("{item[0]}"),
                id="package_select",
                item_id_getter=lambda item: item[1],
                items="packages",
                on_click=on_package_selected,
            ),
        ),
        getter=get_packages_data,
        state=RegistrationSG.package_selection,
    ),
    
    # Окно ввода имени
    Window(
        Const("Введите ваше имя:\n\nПример: Иван"),
        TextInput(
            id="first_name_input",
            on_success=on_first_name_input,
        ),
        state=RegistrationSG.first_name,
    ),
    
    # Окно ввода фамилии
    Window(
        Const("Введите вашу фамилию:\n\nПример: Иванов"),
        TextInput(
            id="last_name_input", 
            on_success=on_last_name_input,
        ),
        state=RegistrationSG.last_name,
    ),
    
    # Окно вопроса об участии в МБ ранее
    Window(
        Const("Участвовал ли ты в МБ ранее?"),
        Column(
            Button(
                Const("Да"),
                id="participated_yes",
                on_click=on_participated_yes,
            ),
            Button(
                Const("Нет"),
                id="participated_no", 
                on_click=on_participated_no,
            ),
        ),
        state=RegistrationSG.participated_before,
    ),
    
    # Окно ввода года участия
    Window(
        Const("В каком году ты участвовал в МБ?"),
        TextInput(
            id="participation_year_input",
            on_success=on_participation_year_input,
        ),
        state=RegistrationSG.participation_year,
    ),
    
    # Окно вопроса о выпускнике ВШМ
    Window(
        Const("Ты выпускник ВШМ?"),
        Column(
            Button(
                Const("Да"),
                id="vsm_graduate_yes",
                on_click=on_vsm_graduate_yes,
            ),
            Button(
                Const("Нет"),
                id="vsm_graduate_no",
                on_click=on_vsm_graduate_no,
            ),
        ),
        state=RegistrationSG.is_vsm_graduate,
    ),
    
    # Окно ввода года выпуска
    Window(
        Const("В каком году ты окончил ВШМ?"),
        TextInput(
            id="graduation_year_input",
            on_success=on_graduation_year_input,
        ),
        state=RegistrationSG.graduation_year,
    ),
    
    # Окно завершения
    Window(
        Const(COMPLETION_TEXT),
        state=RegistrationSG.completed,
    ),
)