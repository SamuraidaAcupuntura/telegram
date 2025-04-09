import logging
import os
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes, MessageHandler, filters
)
from openai import AsyncOpenAI
from dotenv import load_dotenv
import httpx
from telegram.helpers import escape_markdown

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = os.getenv("BASE_URL")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.message.chat_id

    logger.info(f"Mensagem recebida: {user_message}")

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    thread = await client.beta.threads.create()
    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )

    run = await client.beta.threads.runs.create(thread_id=thread.id, assistant_id=os.getenv("ASSISTANT_ID"))

    while True:
        run_status = await client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status == "completed":
            break
        await asyncio.sleep(1)

    messages = await client.beta.threads.messages.list(thread_id=thread.id)
    resposta = messages.data[0].content[0].text.value

    await context.bot.send_message(chat_id=chat_id, text=escape_markdown(resposta, version=2), parse_mode="MarkdownV2")


async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Iniciando o bot...")

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"{BASE_URL}"
    )

if __name__ == "__main__":
    asyncio.run(main())
