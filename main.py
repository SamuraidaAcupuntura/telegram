import logging
import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
import openai
import asyncio

# Carrega variáveis de ambiente
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Inicializa OpenAI com header do v2
client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função que lida com mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text
        logger.info(f"Mensagem recebida: {user_input}")
        await update.message.reply_text("Escrevendo...")

        # Cria thread
        thread = client.beta.threads.create()

        # Adiciona mensagem do usuário
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Roda o assistente
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Espera a conclusão
        while True:
            status = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            await asyncio.sleep(1)

        # Lê resposta final
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value

        await update.message.reply_text(resposta + "\n\nOssu.")
    
    except Exception as e:
        logger.error("Erro ao responder:", exc_info=e)
        await update.message.reply_text("Algo deu errado no dojo. Tente novamente.")

# Função principal
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.bot.set_webhook(WEBHOOK_URL)
    logging.info("Webhook definido com sucesso!")

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL,
    )

# Executa
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
