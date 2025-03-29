import os
from dotenv import load_dotenv
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import httpx
import asyncio
import nest_asyncio

nest_asyncio.apply()
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not TELEGRAM_TOKEN or not OPENAI_API_KEY or not ASSISTANT_ID or not WEBHOOK_URL:
    raise ValueError("Variáveis de ambiente não encontradas. Verifique seu .env.")

logging.basicConfig(level=logging.INFO)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logging.info(f"Mensagem recebida: {user_message}")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            thread_response = await client.post("https://api.openai.com/v1/threads", headers=headers)
            thread_response.raise_for_status()
            thread_id = thread_response.json()["id"]

            message_payload = {"role": "user", "content": user_message}
            await client.post(f"https://api.openai.com/v1/threads/{thread_id}/messages", headers=headers, json=message_payload)

            run_payload = {"assistant_id": ASSISTANT_ID}
            run_response = await client.post(f"https://api.openai.com/v1/threads/{thread_id}/runs", headers=headers, json=run_payload)
            run_response.raise_for_status()

            await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ Mensagem recebida! Aguarde a resposta do assistente.")

        except Exception as e:
            logging.error(f"Erro ao gerar resposta: {e}")
            await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ Erro ao processar sua mensagem.")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    asyncio.run(main())
