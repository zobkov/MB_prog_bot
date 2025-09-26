import gspread
from google.oauth2.service_account import Credentials
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from bot.models import User

logger = logging.getLogger(__name__)

class GoogleSheetsService:
    """Сервис для работы с Google Sheets"""
    
    def __init__(self, credentials_path: str, spreadsheet_url: str):
        self.credentials_path = credentials_path
        self.spreadsheet_url = spreadsheet_url
        self.client = None
        self.sheet = None
        self._setup_client()
    
    def _setup_client(self):
        """Настройка клиента Google Sheets"""
        try:
            # Области доступа для Google Sheets API
            scope = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Загрузка учетных данных
            creds = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=scope
            )
            
            # Создание клиента
            self.client = gspread.authorize(creds)
            
            # Открытие таблицы по URL
            self.sheet = self.client.open_by_url(self.spreadsheet_url).worksheet('main')
            
            logger.info("✅ Подключение к Google Sheets установлено")
            
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Google Sheets: {e}")
            raise
    
    def add_user_to_sheet(self, user: User) -> bool:
        """
        Добавление пользователя в Google Sheets
        
        Args:
            user: Объект пользователя из базы данных
            
        Returns:
            bool: True если успешно добавлено, False если ошибка
        """
        try:
            if not self.sheet:
                logger.error("Google Sheets не инициализирован")
                return False
            
            # Подготовка данных для строки
            row_data = [
                user.id,  # A: ID
                user.telegram_id,  # B: Telegram ID
                f"@{user.username}" if user.username else "Нет username",  # C: Username
                user.first_name,  # D: Имя
                user.last_name,  # E: Фамилия
                self._get_package_name(user.package_type),  # F: Пакет участия
                "Да" if user.participated_before else "Нет",  # G: Участвовал ранее
                user.participation_year or "",  # H: Год участия
                "Да" if user.is_vsm_graduate else "Нет",  # I: Выпускник ВШМ
                user.graduation_year or "",  # J: Год выпуска
                self._format_datetime(user.created_at),  # K: Дата регистрации
                self._format_datetime(user.updated_at),  # L: Дата обновления
            ]
            
            # Проверка, существует ли пользователь в таблице
            existing_row = self._find_user_row(user.telegram_id)
            
            if existing_row:
                # Обновление существующей строки
                self.sheet.update(f'A{existing_row}:L{existing_row}', [row_data])
                logger.info(f"✅ Обновлен пользователь {user.telegram_id} в строке {existing_row}")
            else:
                # Добавление новой строки
                self.sheet.append_row(row_data)
                logger.info(f"✅ Добавлен новый пользователь {user.telegram_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка при добавлении в Google Sheets: {e}")
            return False
    
    def _find_user_row(self, telegram_id: int) -> Optional[int]:
        """
        Поиск строки пользователя по Telegram ID
        
        Args:
            telegram_id: ID пользователя в Telegram
            
        Returns:
            int: Номер строки или None если не найден
        """
        try:
            # Получаем все значения из колонки B (Telegram ID)
            telegram_ids = self.sheet.col_values(2)  # Колонка B
            
            # Ищем соответствующий telegram_id
            for i, cell_value in enumerate(telegram_ids, 1):
                if cell_value == str(telegram_id):
                    return i
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Ошибка при поиске пользователя: {e}")
            return None
    
    def _get_package_name(self, package_type: str) -> str:
        """Получение читаемого названия пакета"""
        package_names = {
            'gala': '🎪 Гала-ужин (10,000₽)',
            'dinner': '🍽️ Ужин (7,000₽)',
            'afterparty': '🎉 Афтепати (3,000₽)'
        }
        return package_names.get(package_type, package_type)
    
    def _format_datetime(self, dt: Optional[datetime]) -> str:
        """Форматирование даты и времени для Google Sheets"""
        if dt is None:
            return ""
        return dt.strftime("%d.%m.%Y %H:%M")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Получение статистики из Google Sheets
        
        Returns:
            dict: Словарь со статистикой
        """
        try:
            if not self.sheet:
                return {"error": "Google Sheets не инициализирован"}
            
            # Получаем все записи (пропускаем заголовок)
            all_records = self.sheet.get_all_records()
            
            total_users = len(all_records)
            
            # Подсчет по пакетам
            packages = {}
            participated_before = 0
            vsm_graduates = 0
            
            for record in all_records:
                # Статистика по пакетам
                package = record.get('Пакет участия', '')
                if 'Гала-ужин' in package:
                    packages['gala'] = packages.get('gala', 0) + 1
                elif 'Ужин' in package:
                    packages['dinner'] = packages.get('dinner', 0) + 1
                elif 'Афтепати' in package:
                    packages['afterparty'] = packages.get('afterparty', 0) + 1
                
                # Остальная статистика
                if record.get('Участвовал ранее') == 'Да':
                    participated_before += 1
                
                if record.get('Выпускник ВШМ') == 'Да':
                    vsm_graduates += 1
            
            return {
                "total_users": total_users,
                "packages": packages,
                "participated_before": participated_before,
                "vsm_graduates": vsm_graduates
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка при получении статистики: {e}")
            return {"error": str(e)}