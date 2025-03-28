import os
import logging
import openai
import httpx
import asyncio

from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa cliente OpenAI com HEADERS para usar a versão v2
client = openai.AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

# Função para lidar com mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.chat.type != "private":
            return  # Ignora grupos

        user_input = update.message.text
        logging.info(f"Mensagem recebida: {user_input}")

        # Mostra "escrevendo..."
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        # Cria thread do Assistente
        thread = await client.beta.threads.create()

        # Envia a mensagem para o thread
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Roda o assistente
        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Espera o run terminar
        while True:
            run_status = await client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if run_status.status == "completed":
                break
            await asyncio.sleep(1)

        # Busca as mensagens da thread
        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value

        # Envia a resposta com "Ossu!" no fim
        await update.message.reply_text(resposta + "\n\nOssu!")

    except Exception as e:
        logger.error("Erro ao responder:", exc_info=True)
        await update.message.reply_text("Algo deu errado no dojo. Tente novamente.\n\nOssu!")

# Função principal
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Adiciona handler de mensagens
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Define o webhook
    async with httpx.AsyncClient() as client_http:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
        await client_http.post(url, params={"url": WEBHOOK_URL})
        logging.info("Webhook definido com sucesso!")

    # Inicia o bot
    await app.run_webhook(
        listen="0.0.0.0",
        port=10000,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    asyncio.run(main())
