from aiogram.types import InlineQueryResultArticle, InputTextMessageContent, InlineQuery
from loguru import logger

from src import config


async def default_result(gt):
    return InlineQueryResultArticle(
        id='1',
        title=gt.inline.title,
        description=gt.inline.description,
        input_message_content=InputTextMessageContent(
            message_text=gt.inline.message_text.replace('BOT_USERNAME', config.BOT_USERNAME)),
        thumbnail_url='https://ih1.redbubble.net/image.5356383805.5149/st,small,507x507-pad,600x600,f8f8f8.u1.jpg'
    )


async def handle_inline_query(query: InlineQuery, gt):
    try:
        await query.answer(
            results=[await default_result(gt)],
            switch_pm_text=gt.inline.bot,
            switch_pm_parameter="Inline"
        )
        return
    except Exception as e:
        logger.error(e)