import re
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from loguru import logger


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            db_data, _sub, _settings = None, None, None
            
            # Тут має бути запрос в бд який дістає дані користувача db_data, підписку якщо потрібна _sub, а також налаштування чату _settings, та записує в data
            
            if db_data:
                data['db'] = {
                    'DATA': db_data,
                    'SUB': _sub,
                    'SETTINGS': _settings
                }
                data['lang'] = db_data.get('locale', 'en')
        except Exception as e:
            logger.error(e)
        result = await handler(event, data)
        return result