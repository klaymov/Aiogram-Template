import yaml
import aiofiles
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from loguru import logger

class Translation:
    def __init__(self, translations: dict):
        self._translations = translations

    def __getattr__(self, name: str) -> Any:
        if name in self._translations:
            value = self._translations[name]
            if isinstance(value, dict):
                return Translation(value)
            return value
        raise AttributeError(f"Translation key '{name}' not found")

    def __getitem__(self, key: str) -> Any:
        if key in self._translations:
            value = self._translations[key]
            if isinstance(value, dict):
                return Translation(value)
            return value
        raise KeyError(f"Translation key '{key}' not found")

async def get_translation(language: str) -> Translation:
    try:
        async with aiofiles.open(f'locales/{language}.yaml', mode='r', encoding='utf-8') as f:
            contents = await f.read()
            translations = yaml.safe_load(contents)
            return Translation(translations)
    except FileNotFoundError:
        try:
            async with aiofiles.open(f'locales/uk.yaml', mode='r', encoding='utf-8') as f:
                contents = await f.read()
                translations = yaml.safe_load(contents)
                return Translation(translations)
        except:
            raise ValueError(f'Language file for {language} not found..')
        # raise ValueError(f'Language file for {language} not found')
    except yaml.YAMLError:
        raise RuntimeError('Error parsing YAML file')

class LocaleMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        try:
            lang = data['lang'] if 'lang' in data else 'en'
            gt = await get_translation(lang)
            data['gt'] = gt
        except Exception as e:
            logger.error(e)
        
        result = await handler(event, data)
        return result