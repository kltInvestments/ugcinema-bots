from telethon import TelegramClient
from .config import settings

def make_client(session_name: str):
    return TelegramClient(session_name, settings.API_ID, settings.API_HASH)
