from aiogram.fsm.state import State, StatesGroup


class RegistrationSG(StatesGroup):
    # Приветствие
    welcome = State()
    
    # Выбор пакета
    package_selection = State()
    
    # Ввод имени
    first_name = State()
    
    # Ввод фамилии  
    last_name = State()
    
    # Участвовал ли раньше в МБ
    participated_before = State()
    
    # Год участия (если участвовал)
    participation_year = State()
    
    # Выпускник ли ВШМ
    is_vsm_graduate = State()
    
    # Год выпуска (если выпускник)
    graduation_year = State()
    
    # Завершение
    completed = State()