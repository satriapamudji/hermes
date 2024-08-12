from telethon import TelegramClient
from config.settings import API_ID, API_HASH

client = TelegramClient('hermes', API_ID, API_HASH)
__all__ = ['client']