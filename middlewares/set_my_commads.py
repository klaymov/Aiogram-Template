from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, Message, BotCommand, BotCommandScopeChat
from loguru import logger


class SetCommandsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        message: Message,
        data: Dict[str, Any]
    ) -> Any:
        result = await handler(message, data)
        try:
            chat_id = message.chat.id
            gt = data['gt']
            bot = data['bot']
            
            if message.chat.type == 'private':
                await set_private_commands(bot, chat_id, gt)
            else:
                await set_group_commands(bot, chat_id, gt)
                
        except Exception as e:
            logger.error(f"Error setting commands: {e}")
            
        return result


async def set_private_commands(bot: Bot, chat_id, gt):
    commands = [BotCommand(command='help', description=gt.commandscope.help),
                BotCommand(command='privacy', description=gt.commandscope.privacy),
                BotCommand(command='donate', description=gt.commandscope.donate)
                ]
    await bot.set_my_commands(
        commands=commands, 
        scope=BotCommandScopeChat(chat_id=chat_id))


async def set_group_commands(bot: Bot, chat_id, gt):
    commands = [BotCommand(command='settings', description=gt.commandscope.settings),
                BotCommand(command='premium', description=gt.commandscope.premium)
                ]
    await bot.set_my_commands(
        commands=commands, 
        scope=BotCommandScopeChat(chat_id=chat_id))