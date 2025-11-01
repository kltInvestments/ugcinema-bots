from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import asyncio

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("\u2705 Uploader bot is online.")

async def main():
    token = os.environ.get("UPLOADER_BOT_TOKEN")
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

if __name__ == "__main__":
    asyncio.run(main())
