import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os
import nest_asyncio

BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
APP_URL = "https://telegram-wsro.onrender.com"

# Habilita múltiplos loops assíncronos (necessário no Render)
nest_asyncio.apply()

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Opa, Samurai aqui! Pronto pra servir. 🥷")

# Roda o bot com webhook
async def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handler do /start
    app.add_handler(CommandHandler("start", start))

    # Define o webhook com a rota correta
    webhook_url = f"{APP_URL}/webhook"
    await app.bot.set_webhook(url=webhook_url)

    print("Bot iniciado com webhook!")
    
    # Roda o servidor webhook ouvindo na rota correta
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=webhook_url,
        path="/webhook"
    )

if __name__ == "__main__":
    asyncio.run(main())
