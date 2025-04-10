import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI

TOKEN_TELEGRAM = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ASSISTANT_ID = os.getenv('ASSISTANT_ID')

openai_client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Samurai Bot online.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        thread = openai_client.beta.threads.create()
        openai_client.beta.threads.messages.create(thread_id=thread.id, role="user", content=user_message)

        run = openai_client.beta.threads.runs.create(thread_id=thread.id, assistant_id=ASSISTANT_ID)

        while run.status in ["queued", "in_progress"]:
            run = openai_client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

        messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value

        await update.message.reply_text(resposta)

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text("⚠️ Ocorreu um erro ao gerar resposta.")

if __name__ == '__main__':
    import asyncio
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    asyncio.run(app.run_polling())
