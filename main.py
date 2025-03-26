import logging
import asyncio
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import openai
import os

# Configurações iniciais
openai.api_key = "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"
ALLOWED_USERS = ["paulocosta@samuraidaacupuntura.com.br", "andreiabioterapia@hotmail.com"]

# Ativa logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para simular digitação
async def send_typing_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, delay: float = 0.7):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(delay)

    sentences = text.split(". ")
    for sentence in sentences:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=sentence.strip())
        await asyncio.sleep(delay)

    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ossu")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and user.username and user.username.lower() in [email.split("@")[0].lower() for email in ALLOWED_USERS]:
        welcome_text = "Saudações, guerreiro. Você está conectado ao assistente do Samurai. Preparado para a Jornada?"
        await send_typing_text(update, context, welcome_text)
    else:
        await update.message.reply_text("Acesso negado. Você não está autorizado. Contate o Samurai.")

# Comando /ask para perguntar algo ao ChatGPT
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user and user.username and user.username.lower() in [email.split("@")[0].lower() for email in ALLOWED_USERS]:
        question = " ".join(context.args)
        if not question:
            await update.message.reply_text("Envie uma pergunta após o comando /ask.")
            return

        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente do Samurai da Acupuntura."},
                    {"role": "user", "content": question},
                ]
            )
            reply = response.choices[0].message.content
            await send_typing_text(update, context, reply)
        except Exception as e:
            logger.error(f"Erro ao consultar OpenAI: {e}")
            await update.message.reply_text("Houve um erro ao consultar o oráculo. Tente novamente.")
    else:
        await update.message.reply_text("Acesso negado. Você não está autorizado. Contate o Samurai.")

# Inicialização
if __name__ == '__main__':
    application = ApplicationBuilder().token("7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ask", ask))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url="https://telegram-wsro.onrender.com"
    )
