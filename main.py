import os
import asyncio
import logging

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)
import httpx
from openai import AsyncOpenAI

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variáveis de ambiente
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not all([TELEGRAM_TOKEN, OPENAI_API_KEY, OPENAI_ASSISTANT_ID, WEBHOOK_URL]):
    raise ValueError("⚠️ Variáveis de ambiente não encontradas. Verifique seu .env.")

# Cliente OpenAI
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Função para processar mensagens
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.text:
        user_input = update.message.text
        logger.info(f"Mensagem recebida: {user_input}")

        try:
            thread = await client.beta.threads.create()
            await client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=user_input,
            )
            run = await client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=OPENAI_ASSISTANT_ID,
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
            await update.message.reply_text(resposta)

        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            await update.message.reply_text("⚠️ Ocorreu um erro ao processar a mensagem.")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Sou o assistente do Samurai da Acupuntura. Como posso ajudar?")

# Função principal
async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    await application.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=WEBHOOK_URL,
    )

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
