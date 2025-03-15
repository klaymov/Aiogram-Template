from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message
from cachetools import TTLCache


class ThrottlingMiddleware(BaseMiddleware):
    """
    Затримка 2 сек між повідомленнями
    """
    def __init__(self, ttl: int = 2):
        self.ttl = ttl
        self.cache = TTLCache(maxsize=10_000, ttl=ttl)
        self.first_message = set()

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        # Якщо це перше повідомлення від користувача
        if event.chat.id not in self.first_message:
            self.first_message.add(event.chat.id)
            return await handler(event, data)
        
        # Перевірка на спам
        if event.chat.id in self.cache:
            return
        
        self.cache[event.chat.id] = None
        return await handler(event, data)