import os
import logging
import asyncio
import re
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def dividir_em_frases(texto):
    return re.split(r'(?<=[.!?]) +', texto.strip())

async def responder_por_frase(texto, update: Update, context: ContextTypes.DEFAULT_TYPE):
    frases = dividir_em_frases(texto)
    for frase in frases:
        if frase.strip():
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            await asyncio.sleep(1.2)
            if update.message:
    await update.message.reply_text(frase.strip())
else:
    await context.bot.send_message(chat_id=update.effective_chat.id, text=frase.strip())


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Mensagem recebida: {user_message}")

    try:
        thread = await client.beta.threads.create()
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message,
        )
        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=os.getenv("OPENAI_ASSISTANT_ID"),
        )

        while True:
            run_status = await client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            if run_status.status == "completed":
                break
            await asyncio.sleep(1)

        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value
        await responder_por_frase(resposta, update, context)

    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {e}")
        await update.message.reply_text("Ocorreu um erro ao gerar a resposta. Tente novamente mais tarde.")

async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Iniciando o bot...")
    await application.bot.set_webhook(url=WEBHOOK_URL)
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
