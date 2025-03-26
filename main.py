import os
import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
import nest_asyncio

# Configurações
BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
APP_URL = "https://telegram-wsro.onrender.com"

# Necessário no Render
nest_asyncio.apply()

# Log
logging.basicConfig(level=logging.INFO)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Opa, Samurai aqui! Pronto pra servir. 🥷")

# Função principal
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Adiciona comando
    app.add_handler(CommandHandler("start", start))

    # Define webhook
    await app.bot.set_webhook(url=f"{APP_URL}/webhook")

    print("Bot iniciado com webhook!")

    # Inicia servidor webhook
await app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 10000)),
    webhook_url=f"{APP_URL}/webhook"
)


# Executa
if __name__ == "__main__":
    asyncio.run(main())
