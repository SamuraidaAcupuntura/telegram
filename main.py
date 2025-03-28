import os
import logging
import openai
import httpx
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, ContextTypes, MessageHandler, filters

# Corrige erro de loop já rodando
nest_asyncio.apply()

# Carrega variáveis do .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID", "asst_JuGSeUFtvvkiSCfav4LNQUqw")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cliente OpenAI v2
client = openai.AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

# Função para responder mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.chat.type != "private":
            return

        user_input = update.message.text
        logger.info(f"Mensagem recebida: {user_input}")

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        thread = await client.beta.threads.create()

        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        while True:
            status = await client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            await asyncio.sleep(1)

        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value.strip()

        await update.message.reply_text(resposta + "\n\nOssu!")

    except Exception as e:
        logger.error("Erro ao responder:", exc_info=True)
        await update.message.reply_text("Algo deu errado no dojo. Tente novamente.\n\nOssu!")

# Inicialização
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    async with httpx.AsyncClient() as client_http:
        await client_http.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
            params={"url": WEBHOOK_URL}
        )
        logger.info("Webhook definido com sucesso!")

    await app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    asyncio.run(main())
