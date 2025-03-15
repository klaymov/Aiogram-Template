from aiogram import Router, F
from aiogram.filters import Command
from loguru import logger

from src.config import ADMIN_ID
from . import (
    base,
    ping,
    inline
    )


def get_handlers_router() -> Router:
    router = Router()
    
    # роутер для приватних повідомлень
    private_router = Router()
    private_router.message.filter(F.chat.type == "private")
    
    #
    admin_router = Router()
    admin_router.message.filter(F.chat.type != "private")
    admin_router.message.filter(F.from_user.id == int(ADMIN_ID))
    # адмін роутер для адмінки
    
    router.inline_query()(inline.handle_inline_query)
    
    private_router.message(Command('start'))(base.command_start)
    private_router.message(Command('privacy'))(base.privacy_policy)
    private_router.message(Command('support'))(base.support)
    private_router.message(Command('help'))(base.help)
    
    router.message(Command('ping'))(ping.ping_command)
    router.message(Command('cat'))(base.cat)

    
    router.include_routers(
        private_router,
        admin_router
        )
    logger.info("Hadlers successfully loaded and started")
    return router