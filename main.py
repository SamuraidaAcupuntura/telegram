import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI

# Configurações
BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
APP_URL = "https://telegram-wsro.onrender.com"
OPENAI_API_KEY = "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"

# Inicializando o client da OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Comandos
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Pode me mandar uma pergunta 🧠")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente que responde com base na Medicina Chinesa e sabedoria do Samurai da Acupuntura."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = completion.choices[0].message.content
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Erro com OpenAI: {e}")
        await update.message.reply_text("Desculpe, ocorreu um erro ao buscar a resposta. 🙏")

# Inicialização principal
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Configurando o Webhook
    webhook_url = f"{APP_URL}/webhook"
    await app.bot.set_webhook(url=webhook_url)
    logger.info("Webhook definido com sucesso!")
    
    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=webhook_url,
    )

if __name__ == "__main__":
    asyncio.run(main())
