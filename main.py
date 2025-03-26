import os
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from openai import OpenAI

# Configurações
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.environ.get('PORT', '8080'))
URL = os.getenv("RENDER_EXTERNAL_URL")

# OpenAI client (versão nova)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para responder
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    try:
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        resposta = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um mentor sábio chamado Samurai da Acupuntura."},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        conteudo = resposta.choices[0].message.content if resposta.choices else "⚠️ Sem resposta gerada."
        await update.message.reply_text(conteudo.strip() + "\n\nossu.")

    except Exception as e:
        logger.error(f"Erro interno: \n{e}")
        await update.message.reply_text("⚠️ Tive um problema interno ao responder. Verifique sua chave da OpenAI ou o modelo.\n\nossu.")

# App
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).webhook_url(f"{URL}/webhook").build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url=f"{URL}/webhook")
