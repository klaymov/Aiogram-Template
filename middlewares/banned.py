from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from loguru import logger

from locales import get_translation as _

class BannedMiddleware(BaseMiddleware):
    """
    Мідлварь на перевірку чи забанений користувач
    """
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            if event.message:
                if event.message.chat.type == "private":
                    if data['db']['DATA'].get('banned'):
                        text = await _(data['lang'], 'banned')
                        await event.message.bot.send_message(event.message.from_user.id, text)
                        return
        except Exception as e:
            logger.error(e)
        result = await handler(event, data)

        return result