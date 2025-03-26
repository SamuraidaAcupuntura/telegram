import logging
import os
from telegram.ext import Application, CommandHandler
from openai import OpenAI

# Chaves e tokens
BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
OPENAI_API_KEY = "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"
APP_URL = "https://telegram-bot-gpt.render.com"  # substitua pela URL real do seu app no Render

# Configurar logs
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Cliente OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Comando /start
async def start(update, context):
    await update.message.reply_text("Oss! Eu sou o assistente do Samurai da Acupuntura.")

# Inicialização do bot
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    PORT = int(os.environ.get("PORT", 5000))
    await application.bot.delete_webhook()
    await application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{APP_URL}/{BOT_TOKEN}",
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
