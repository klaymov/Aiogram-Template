from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer 

from .config import BOT_TOKEN, LOCAL_BOT_API

try:
    raise # приберіть raise щоб використовувати локал бот апі
    session = AiohttpSession(api=TelegramAPIServer.from_base(LOCAL_BOT_API, is_local=True))
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML), session=session)
    dp = Dispatcher()
except:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()