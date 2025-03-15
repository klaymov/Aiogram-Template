from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from loguru import logger


class CheckKickedMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            # if event.new_chat_member:
            #     ...
            if event.message:
                """
                Видалення групи з бд
                """
                if event.message.chat.type == "group" or event.message.chat.type == "supergroup":
                    if hasattr(event.message, 'left_chat_participant') and event.message.left_chat_participant:
                        if event.message.left_chat_participant.get('id') == event.bot.id:
                            # Видалення з бд
                            return
                        
        except Exception as e:
            logger.error(e)
        result = await handler(event, data)

        return result