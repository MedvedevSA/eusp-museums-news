from pydantic import BaseSettings


class Setting(BaseSettings):
    DB_HOST: str = 'localhost'
    DB_PORT: int = 5432
    DB_DATABASE: str = 'postgres'
    DB_USER: str = 'postgres'
    DB_PASSWORD: str = 'qweASDzxc'
    REDIS_HOST = 'localhost'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Setting()

DB_URL = '{}:{}@{}:{}/{}'.format(
    settings.DB_USER,
    settings.DB_PASSWORD,
    settings.DB_HOST,
    settings.DB_PORT,
    settings.DB_DATABASE,
)
ASYNC_DB_URL = f'postgresql+asyncpg://{DB_URL}'
SYNC_DB_URL = f'postgresql://{DB_URL}'