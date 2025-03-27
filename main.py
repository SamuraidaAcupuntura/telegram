import logging
import os
import openai
from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import httpx
import asyncio

# Carrega variáveis do .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Inicializa o cliente OpenAI com o cabeçalho correto para Assistants v2
client = openai.AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

# Configura o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para lidar com mensagens recebidas
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    logger.info(f"Mensagem recebida: {user_input}")
    
    try:
        await update.message.reply_text("Escrevendo...")

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
            run_status = await client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            await asyncio.sleep(1)

        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value

        await update.message.reply_text(resposta + "\n\nOssu.")

    except Exception as e:
        logger.error("Erro ao responder:", exc_info=e)
        try:
            await update.message.reply_text("Algo deu errado no dojo. Tente novamente.")
        except:
            pass

# Função principal da aplicação
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

# Execução
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
