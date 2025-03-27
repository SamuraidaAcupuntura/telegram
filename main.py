import logging
import os
import openai
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import httpx

load_dotenv()

# Configurações:
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
print("TOKEN CARREGADO:", TELEGRAM_TOKEN)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

openai.api_key = OPENAI_API_KEY

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Função para lidar com mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    await update.message.reply_text("Escrevendo...")

    try:
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Aguarda a conclusão do processamento
        while True:
            run_check = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_check.status == "completed":
                break

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value
        await update.message.reply_text(resposta + "\n\nOssu.")

    except Exception as e:
        logger.error("Erro:", exc_info=e)
        await update.message.reply_text("Algo deu errado no dojo. Tente novamente.")

# Main async
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.bot.set_webhook(WEBHOOK_URL)
    logging.info("Webhook definido com sucesso!")

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    import asyncio
    import nest_asyncio

    nest_asyncio.apply()
    asyncio.get_event_loop().run_until_complete(main())

