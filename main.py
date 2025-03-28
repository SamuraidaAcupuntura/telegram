import os
import logging
import asyncio
import openai
import httpx

from telegram import Update, ChatAction, InputFile
from telegram.ext import Application, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cliente OpenAI com headers para Assistants v2
client = openai.AsyncOpenAI(
    api_key=OPENAI_API_KEY,
    default_headers={"OpenAI-Beta": "assistants=v2"}
)

# Função de digitação simulada (linha a linha)
async def enviar_resposta_lenta(chat, resposta: str, context):
    for linha in resposta.split("\n"):
        if linha.strip():
            await context.bot.send_chat_action(chat_id=chat, action=ChatAction.TYPING)
            await asyncio.sleep(0.8)
            await context.bot.send_message(chat_id=chat, text=linha)
    await context.bot.send_message(chat_id=chat, text="Ossu!")

# Tratador de mensagens de texto
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

        # Espera até que a resposta esteja pronta
        while True:
            status = await client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
            if status.status == "completed":
                break
            await asyncio.sleep(1)

        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value
        await enviar_resposta_lenta(update.effective_chat.id, resposta, context)

    except Exception as e:
        logger.error("Erro ao responder:", exc_info=True)
        await update.message.reply_text("Algo deu errado no dojo. Tente novamente.\n\nOssu!")

# Tratador de arquivos
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return

    arquivo = update.message.document or update.message.photo[-1] if update.message.photo else None
    if not arquivo:
        await update.message.reply_text("Não consegui entender o tipo de arquivo.\n\nOssu!")
        return

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await update.message.reply_text("Recebi seu arquivo. No momento ainda não interpreto conteúdo de documentos, mas posso guiá-lo com base em perguntas. Me diga o que deseja!\n\nOssu!")

# Função principal que retorna a instância do app (usada no uvicorn)
async def create_app():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))

    async with httpx.AsyncClient() as client_http:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook"
        await client_http.post(url, params={"url": WEBHOOK_URL})
        logger.info("Webhook definido com sucesso!")

    return app

# Executa o app com Webhook
if __name__ == "__main__":
    import nest_asyncio
    from telegram.ext._application import Application

    nest_asyncio.apply()

    async def run_bot():
        app = await create_app()
        await app.run_webhook(
            listen="0.0.0.0",
            port=10000,
            webhook_url=WEBHOOK_URL
        )

    asyncio.run(run_bot())
