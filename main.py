import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
import httpx
import json

# Carregar variáveis do .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not all([TELEGRAM_TOKEN, OPENAI_API_KEY, ASSISTANT_ID, WEBHOOK_URL]):
    raise ValueError("Variáveis de ambiente não encontradas. Verifique seu .env.")

# Setup logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Eu sou o Samurai da Acupuntura. Como posso ajudar?")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = update.message.text
    logger.info(f"Mensagem recebida: {mensagem}")

    async with httpx.AsyncClient() as client:
        thread = await client.post(
            "https://api.openai.com/v1/threads",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
        )
        thread_id = thread.json().get("id")

        await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"role": "user", "content": mensagem}
        )

        run = await client.post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"assistant_id": ASSISTANT_ID}
        )

        if run.status_code != 200:
            logger.error("Erro ao iniciar execução do assistente")
            await update.message.reply_text("Ocorreu um erro ao processar sua mensagem.")
            return

        # Esperar resposta finalizada
        run_id = run.json()["id"]
        while True:
            status = await client.get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
            )
            if status.json()["status"] == "completed":
                break
            await asyncio.sleep(1)

        messages = await client.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
        )
        resposta = messages.json()["data"][0]["content"][0]["text"]["value"]
        await update.message.reply_text(resposta)

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    await app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
