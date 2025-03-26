import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Ativa o suporte a múltiplas chamadas de loop
nest_asyncio.apply()

# Seus dados fixos
BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
APP_URL = "https://telegram-wsro.onrender.com"

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Estou vivo com webhook 🚀")

# Função principal
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Comandos
    app.add_handler(CommandHandler("start", start))

    # Define o webhook
    await app.bot.set_webhook(url=f"{APP_URL}/webhook")
    print("Bot iniciado com webhook!")

    # Roda o webhook
    await app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=f"{APP_URL}/webhook"
    )

# Executa o loop assíncrono com nest_asyncio aplicado
asyncio.get_event_loop().run_until_complete(main())
