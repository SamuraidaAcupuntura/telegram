import logging
import os
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Configurações do bot
TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
APP_URL = "https://telegram-wsro.onrender.com"

# Aplicar patch no event loop (necessário no Render)
nest_asyncio.apply()

# Ativar log
logging.basicConfig(level=logging.INFO)

# Comando básico para testar se o bot está vivo
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá, Samurai. Estou vivo!")

# Função principal
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Adiciona o handler do /start
    app.add_handler(CommandHandler("start", start))

    # Define o webhook
    await app.bot.set_webhook(url=f"{APP_URL}/webhook")

    # Inicia o servidor para escutar o webhook
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{APP_URL}/webhook"
    )

# Roda o bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
