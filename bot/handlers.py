from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram_dialog import DialogManager, StartMode
from bot.states import RegistrationSG

router = Router()


@router.message(CommandStart())
async def start_command(message: Message, dialog_manager: DialogManager):
    """Обработчик команды /start"""
    await dialog_manager.start(RegistrationSG.welcome, mode=StartMode.RESET_STACK)


@router.message(Command(commands=['menu']))
async def process_command_menu(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=RegistrationSG.welcome, mode=StartMode.RESET_STACK)