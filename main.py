import logging
import asyncio
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from openai import OpenAI

# Configurações
BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
OPENAI_API_KEY = "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"
WEBHOOK_URL = "https://telegram-wsro.onrender.com"

# Inicializa cliente OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Logs
logging.basicConfig(level=logging.INFO)

# Função para simular digitação e responder em frases
async def send_typing_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    frases = text.split(". ")
    for frase in frases:
        if frase.strip():
            await asyncio.sleep(2)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=frase.strip())
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ossu 🥋")

# Quando recebe mensagem
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}],
    )

    resposta = response.choices[0].message.content
    await send_typing_message(update, context, resposta)

# Função principal
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    main()
