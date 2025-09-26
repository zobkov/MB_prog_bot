import logging
import os
from environs import Env
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    user: str
    password: str
    database: str
    host: str
    port: int = 5432

@dataclass
class RedisConfig:
    password: str
    host: str
    port: int = 6379

@dataclass
class Bot:
    token: str

@dataclass
class Config:
    bot: Bot
    db: DatabaseConfig
    redis: RedisConfig

def load_config(path: str = None) -> Config:
    # Загружаем переменные окружения
    env = Env()
    env.read_env()
    
    bot = Bot(token=env.str("BOT_TOKEN"))
    db = DatabaseConfig(
        user=env.str("DB_USER"),
        password=env.str("DB_PASS"),
        database=env.str("DB_NAME"),
        host=env.str("DB_HOST"),
        port=env.int("DB_PORT", 5432)
    )

    redis = RedisConfig(
        host=env.str("REDIS_HOST"),
        port=env.int("REDIS_PORT", 6379),
        password=env.str("REDIS_PASSWORD", "")
    )
    
    return Config(
        bot=bot,
        db=db,
        redis=redis
    )