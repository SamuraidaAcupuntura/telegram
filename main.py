import os
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import logging

# Configurações
BOT_TOKEN = "7877551847:AAED0zlqMiNgmxC4AIoCJMFSMZmV0evfIXM"
APP_URL = "https://telegram-wsro.onrender.com"
OPENAI_API_KEY = os.environ.get("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")  # chave será lida da variável de ambiente

client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    logging.info(f"Recebido: {user_input}")
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Você é um assistente do Samurai da Acupuntura. Responda com base em Medicina Chinesa e espiritualidade prática."},
            {"role": "user", "content": user_input}
        ]
    )
    await update.message.reply_text(response.choices[0].message.content)

if __name__ == "__main__":
    import nest_asyncio, asyncio
    from telegram.ext import Application

    nest_asyncio.apply()

    async def main():
        app = ApplicationBuilder().token(BOT_TOKEN).build()
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # define webhook
        await app.bot.set_webhook(url=f"{APP_URL}/webhook")
        logging.info("Webhook definido com sucesso!")

        await app.run_webhook(
            listen="0.0.0.0",
            port=8000,
            webhook_url=f"{APP_URL}/webhook"
        )

    asyncio.run(main())
