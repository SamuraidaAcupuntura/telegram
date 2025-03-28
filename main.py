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

# Corrigir problemas de loop em serviços como Render
nest_asyncio.apply()

# Carregar variáveis de ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cliente da OpenAI com headers da API v2
client = openai.AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

# Função para responder mensagens de texto
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
            await asyncio.sleep(0.5)

        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[-1].content[0].text.value.strip()

        for linha in resposta.split("\n"):
            if linha.strip():
                await update.message.reply_text(linha.strip())
                await asyncio.sleep(0.3)

    except Exception as e:
        logger.error("Erro ao responder mensagem:", exc_info=True)
        await update.message.reply_text("⚠️ Erro ao processar. Tente novamente.")

# Função para processar imagens
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.chat.type != "private":
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        file_id = update.message.photo[-1].file_id
        file_info = await context.bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"

        thread = await client.beta.threads.create()
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": file_url
                    }
                }
            ]
        )

        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        while True:
            status = await client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            await asyncio.sleep(0.5)

        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[-1].content[0].text.value.strip()

        for linha in resposta.split("\n"):
            if linha.strip():
                await update.message.reply_text(linha.strip())
                await asyncio.sleep(0.3)

    except Exception as e:
        logger.error("Erro ao processar imagem:", exc_info=True)
        await update.message.reply_text("❌ Não consegui analisar a imagem. Envie novamente ou tente outra.")

# Inicialização do bot
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_image))

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
