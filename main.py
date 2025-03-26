import logging
import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from openai import OpenAI

BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
APP_URL = "https://telegram-wsro.onrender.com"
openai_client = OpenAI(api_key="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")

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Envie sua pergunta com /perguntar.")

async def perguntar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pergunta = ' '.join(context.args)
    if not pergunta:
        await update.message.reply_text("Por favor, envie sua pergunta após /perguntar.")
        return

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente espiritual e profundo."},
            {"role": "user", "content": pergunta}
        ]
    )
    resposta = response.choices[0].message.content
    await update.message.reply_text(resposta)

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("perguntar", perguntar))

    await app.bot.set_webhook(url=f"{APP_URL}/webhook")
    print("Bot iniciado com webhook!")

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{APP_URL}/webhook"
    )

# Correção para ambiente que já tem loop rodando (Render)
try:
    asyncio.get_event_loop().run_until_complete(main())
except RuntimeError:
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())
