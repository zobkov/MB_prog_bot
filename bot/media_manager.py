import json
import os
from typing import Optional
from aiogram import Bot
from aiogram.types import FSInputFile
from aiogram.enums import ContentType
from aiogram_dialog.api.entities import MediaAttachment, MediaId


class MediaManager:
    def __init__(self, bot: Bot, file_ids_path: str = "file_ids.json"):
        self.bot = bot
        # Путь к JSON файлу относительно корня проекта
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.file_ids_path = os.path.join(project_root, file_ids_path)
        self.target_user_id = 257026813  # ID пользователя для отправки и получения file_id
        
    def _load_file_ids(self) -> dict:
        """Загружает file_id из JSON файла"""
        if os.path.exists(self.file_ids_path):
            try:
                with open(self.file_ids_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_file_ids(self, file_ids: dict):
        """Сохраняет file_id в JSON файл"""
        with open(self.file_ids_path, 'w', encoding='utf-8') as f:
            json.dump(file_ids, f, ensure_ascii=False, indent=2)
    
    async def get_file_id(self, filename: str) -> Optional[str]:
        """Получает file_id для файла. Если его нет, генерирует новый"""
        file_ids = self._load_file_ids()
        
        # Проверяем, есть ли уже file_id для этого файла
        if filename in file_ids:
            print(f"✅ Найден существующий file_id для {filename}")
            return file_ids[filename]
        
        # Если file_id нет, генерируем его
        print(f"🔄 Генерация file_id для {filename}...")
        file_id = await self._generate_file_id(filename)
        
        if file_id:
            # Сохраняем новый file_id
            file_ids[filename] = file_id
            self._save_file_ids(file_ids)
            print(f"✅ Сгенерирован и сохранен file_id для {filename}")
            return file_id
        
        return None
    
    async def _generate_file_id(self, filename: str) -> Optional[str]:
        """Генерирует file_id путем отправки файла пользователю"""
        try:
            # Формируем полный путь к файлу (относительно корня проекта)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            full_path = os.path.join(project_root, filename)
            
            # Проверяем существование файла
            if not os.path.exists(full_path):
                print(f"❌ Файл {full_path} не найден")
                return None
            
            # Отправляем файл пользователю
            photo = FSInputFile(full_path)
            message = await self.bot.send_photo(
                chat_id=self.target_user_id,
                photo=photo,
                caption=f"Генерация file_id для {os.path.basename(filename)}"
            )
            
            # Получаем file_id из отправленного сообщения
            if message.photo:
                file_id = message.photo[-1].file_id  # Берем самое большое разрешение
                print(f"✅ Получен file_id: {file_id}")
                return file_id
            
        except Exception as e:
            print(f"❌ Ошибка при генерации file_id для {filename}: {e}")
        
        return None
    
    async def get_media_attachment(self, filename: str) -> Optional[MediaAttachment]:
        """Получает MediaAttachment для файла"""
        file_id = await self.get_file_id(filename)
        if file_id:
            return MediaAttachment(ContentType.PHOTO, file_id=MediaId(file_id))
        return None