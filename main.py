import logging
import os
import asyncio
from dotenv import load_dotenv
import openai
from telegram import Update
from telegram.ext import Application, MessageHandler, ContextTypes, filters

# Carrega variáveis do .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Inicializa cliente OpenAI sem headers
client = openai.AsyncOpenAI(api_key=OPENAI_API_KEY)

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função que responde as mensagens do Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_input = update.message.text
        logger.info(f"Mensagem recebida: {user_input}")
        await update.message.reply_text("Escrevendo...")

        # Cria thread
        thread = await client.beta.threads.create()

        # Envia mensagem do usuário para a thread
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
            headers={"OpenAI-Beta": "assistants=v2"}
        )

        # Cria o run da assistant
        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID,
            headers={"OpenAI-Beta": "assistants=v2"}
        )

        # Aguarda o run finalizar
        while True:
            status = await client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
                headers={"OpenAI-Beta": "assistants=v2"}
            )
            if status.status == "completed":
                break
            await asyncio.sleep(1)

        # Recupera resposta
        messages = await client.beta.threads.messages.list(
            thread_id=thread.id,
            headers={"OpenAI-Beta": "assistants=v2"}
        )
        resposta = messages.data[0].content[0].text.value
        await update.message.reply_text(resposta)

    except Exception as e:
        logger.error("Erro ao responder:", exc_info=e)
        try:
            await update.message.reply_text("Algo deu errado no dojo. Tente novamente.")
        except:
            pass

# Inicializa o bot com webhook
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
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
