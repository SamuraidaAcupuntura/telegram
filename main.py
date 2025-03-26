import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import nest_asyncio

# Configurações
TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
APP_URL = "https://telegram-wsro.onrender.com"

# Ativar logs
logging.basicConfig(level=logging.INFO)

# Comando de /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou o SamuraiBot e estou online!")

# Inicialização
async def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))

    # Ativa o webhook
    await application.bot.set_webhook(url=f"{APP_URL}/webhook")
    logging.info("Webhook definido com sucesso!")

    # Inicia a aplicação via webhook
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{APP_URL}/webhook",
    )

if __name__ == '__main__':
    nest_asyncio.apply()
    import asyncio
    asyncio.run(main())
