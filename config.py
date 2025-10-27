import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    API_ID: int = int(os.getenv("API_ID", "0"))
    API_HASH: str = os.getenv("API_HASH", "")
    UPLOADER_BOT_TOKEN: str = os.getenv("UPLOADER_BOT_TOKEN", "")
    PAYMENT_BOT_TOKEN: str = os.getenv("PAYMENT_BOT_TOKEN", "")
    ANALYTICS_BOT_TOKEN: str = os.getenv("ANALYTICS_BOT_TOKEN", "")

    FREE_CHANNEL_USERNAME: str = os.getenv("FREE_CHANNEL_USERNAME", "")
    PAID_GROUP_ID: int = int(os.getenv("PAID_GROUP_ID", "0"))

    FREE_UPLOADER_ID: int = int(os.getenv("FREE_UPLOADER_ID","0"))
    PAID_UPLOADER_ID: int = int(os.getenv("PAID_UPLOADER_ID","0"))
    TRUSTED_UPLOADER_IDS: list[int] = list(map(int, filter(None, os.getenv("TRUSTED_UPLOADER_IDS","").split(","))))

    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME","")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID","0"))

    SUB_PRICE_UGX: int = int(os.getenv("SUB_PRICE_UGX","3000"))
    SUB_DURATION_DAYS: int = int(os.getenv("SUB_DURATION_DAYS","30"))
    PAYMENT_URL: str = os.getenv("PAYMENT_URL","")

    DATABASE_URL: str = os.getenv("DATABASE_URL","")

    FFMPEG_PRESET: str = os.getenv("FFMPEG_PRESET","veryfast")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL","INFO")

settings = Settings()
