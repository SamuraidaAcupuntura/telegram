import os
import logging
import asyncio
import httpx

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY or not OPENAI_ASSISTANT_ID:
    raise ValueError("⚠️ Variáveis de ambiente não encontradas. Verifique seu .env.")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Mensagem recebida: {user_message}")

    try:
        thread = await client.beta.threads.create()
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message
        )
        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=OPENAI_ASSISTANT_ID
        )

        while True:
            run_status = await client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            await asyncio.sleep(1)

        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        reply = messages.data[0].content[0].text.value.strip()
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao gerar a resposta.")

async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await application.updater.idle()

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
