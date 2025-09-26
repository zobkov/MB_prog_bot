from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram_dialog import DialogManager, StartMode
from bot.states import RegistrationSG

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, dialog_manager: DialogManager):
    """Обработчик команды /start"""
    await dialog_manager.start(RegistrationSG.welcome, mode=StartMode.RESET_STACK)


@router.message(F.text == "/reset")
async def reset_command(message: Message, dialog_manager: DialogManager):
    """Команда для сброса диалога (для тестирования)"""
    await dialog_manager.start(RegistrationSG.welcome, mode=StartMode.RESET_STACK)