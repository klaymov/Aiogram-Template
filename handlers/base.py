import base64
from aiogram.types import Message, URLInputFile
from aiogram.filters import CommandObject

from src.config import SUPPORT_US, BOT_USERNAME


async def start_without_command(message: Message, gt):
    await command_start(message, gt, CommandObject())
    

async def command_start(message: Message, gt, command: CommandObject):
    await message.answer(gt.start.replace('FIRST_USERNAME', message.from_user.first_name).replace('CHANNEL_NAME', 'qublog'))
    await message.answer(gt.start_message)
    
    if command.args:
        try:
            text = base64.b64decode(command.args).decode('utf-8')
        except:
            text = command.args
        # text - можна додати запис реферального айді чи мітки в бд 


async def privacy_policy(message: Message, gt):
    await message.answer(gt.privacy.replace('BOT_USERNAME', BOT_USERNAME))


async def support(message: Message, gt):
    await message.answer(f'{gt.support_text}\n\n@{SUPPORT_US}')


async def help(message: Message, gt):
    await message.answer(gt.help)
    

async def cat(message: Message) -> None:
    await message.reply_photo(URLInputFile('https://cataas.com/cat'))