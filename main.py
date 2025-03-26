import os
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Variáveis de ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
APP_URL = os.getenv("APP_URL")
PORT = int(os.environ.get("PORT", 10000))

# Inicialização do cliente OpenAI com sua chave
client = OpenAI(api_key=OPENAI_API_KEY)

# Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função que chama seu assistente com conhecimento
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pergunta = update.message.text

    try:
        resposta = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é o assistente do Samurai da Acupuntura. Use o tom profundo e simbólico da Jornada do Samurai."},
                {"role": "user", "content": pergunta},
            ]
        )

        texto = resposta.choices[0].message.content
        await update.message.reply_text(texto)

    except Exception as e:
        logger.error(f"Erro com OpenAI: {e}")
        await update.message.reply_text("Ocorreu um erro ao consultar o Samurai 🥷")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Oss 🙏🏼 Sou o assistente do Samurai da Acupuntura. Pode falar comigo.")

# Webhook principal
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    # Configuração do webhook
    await app.initialize()
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{APP_URL}/webhook"
    )
    await app.updater.idle()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
