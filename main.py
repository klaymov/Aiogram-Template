import asyncio
import logging

from loguru import logger
from aiogram import Bot, types
from aiohttp import web
from fastapi import Request, FastAPI, HTTPException

from src.telegram import bot, dp
from src.config import WEBHOOK_PATH, WEBHOOK_URI, BOT_TOKEN, WEBHOOK_PORT
from middlewares import register_middlewares
from handlers import get_handlers_router

LOG_ROTATION_SIZE = "5 MB"
LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}"


def configure_logging() -> None:
    logger.add(
        "logs/bot_logs.log",
        level="DEBUG",
        format=LOG_FORMAT,
        rotation=LOG_ROTATION_SIZE,
        compression="zip",
    )
    
    logging.getLogger('aiogram').setLevel(logging.ERROR)
    logging.getLogger('asyncio').setLevel(logging.ERROR)
    logging.getLogger("uvicorn.access").disabled = True
        

async def log_bot_info(bot: Bot) -> None:
    try:
        bot_info = await bot.get_me()
        status_mapping = {
            True: "Enabled",
            False: "Disabled",
            None: "Unknown"
        }

        bot_attributes = {
            "Name": bot_info.full_name,
            "Username": f"@{bot_info.username}",
            "ID": bot_info.id,
            "Can Join Groups": status_mapping.get(bot_info.can_join_groups, 'N/A'),
            "Privacy Mode": status_mapping.get(not bot_info.can_read_all_group_messages, 'N/A'),
            "Inline Mode": status_mapping.get(bot_info.supports_inline_queries, 'N/A')
        }

        logger.info("Bot Information:")
        for attribute, value in bot_attributes.items():
            logger.info(f"{attribute}: {value}")
        
    except Exception as e:
        logger.error(f"Failed to log bot info: {e}")


async def initialize_bot() -> None:
    
    configure_logging()
    await register_middlewares(dp)
    await log_bot_info(bot)
    
    handlers = get_handlers_router()
    dp.include_routers(handlers)
    
    
async def start_polling() -> None:
    logger.success("Bot started polling")
    await on_shutdown()
    await initialize_bot()
    
    try:
        await dp.start_polling(
            bot,
            skip_updates=True
        )
    except Exception as e:
        logger.error(f"Bot polling error: {e}")
    finally:
        logger.info("Bot stopped")
        

async def handle_webhook_update(request: Request) -> web.Response:
    url = str(request.url)
    token = url[url.rfind('/') + 1:]

    if token == BOT_TOKEN:
        update = types.Update(**await request.json())
        await dp.feed_webhook_update(bot, update)
        return web.Response()
    
    raise HTTPException(status_code=403, detail="Forbidden")


async def on_startup() -> None:
    await on_shutdown()
    await bot.set_webhook(WEBHOOK_URI)
    await initialize_bot()
    logger.success("Bot started webhook")


async def on_shutdown() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.fsm.storage.close()
    await bot.session.close()
    
    
if __name__ == "__main__":
    try:
        raise # приберіть raise щоб використовувати вебхуки
        app = FastAPI()
        
        app.add_event_handler("startup", on_startup)
        app.add_event_handler("shutdown", on_shutdown)

        @app.post(WEBHOOK_PATH)
        async def webhook_endpoint(request: Request):
            return await handle_webhook_update(request)

        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=WEBHOOK_PORT)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        asyncio.run(start_polling())
    except KeyboardInterrupt:
        logger.info("Bot stopped")