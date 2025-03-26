import logging
import os
import openai
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Configuração da sua chave OpenAI
openai.api_key = "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"

# Token do seu bot Telegram
BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"

# Ativando logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para lidar com mensagens
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text

    try:
        # Mostra "digitando..."
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        # Requisição à OpenAI
        resposta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}],
            temperature=0.7,
            max_tokens=1000
        )

        texto_resposta = resposta.choices[0].message.content.strip() + "\n\nossu."
        await update.message.reply_text(texto_resposta)

    except Exception as e:
        logger.error(f"Erro interno: {e}")
        await update.message.reply_text("⚠️ Tive um problema interno ao responder. Verifique sua chave da OpenAI ou o modelo.\n\nossu.")

# Função de /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot Samurai ativado. Envie uma mensagem para começar.\n\nossu.")

# Função principal
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url="https://telegram-wsro.onrender.com"
    )

if __name__ == "__main__":
    main()
