from aiogram import Dispatcher
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from loguru import logger

async def register_middlewares(dp: Dispatcher) -> None:
    from .logging import loggerMiddleware
    from .database import DatabaseMiddleware
    from .throttling import ThrottlingMiddleware
    from .banned import BannedMiddleware
    from .check_kicked import CheckKickedMiddleware
    from .locale import LocaleMiddleware
    from .set_my_commads import SetCommandsMiddleware

    dp.update.outer_middleware(loggerMiddleware()) #logger
    dp.message.middleware(ThrottlingMiddleware()) #анти спам
    dp.callback_query.middleware(CallbackAnswerMiddleware())
    dp.update.middleware(CheckKickedMiddleware()) #перевірка на кік з групи чи блок бота
    dp.update.middleware(DatabaseMiddleware()) #витяг даних з бд
    dp.update.middleware(BannedMiddleware()) #перевірка на бан в боті
    dp.update.middleware(LocaleMiddleware()) #кастомна локалізація
    dp.message.middleware(SetCommandsMiddleware()) #меню команд

    logger.info("Middlewares registered")