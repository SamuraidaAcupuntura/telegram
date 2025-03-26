import logging
import asyncio
from telegram import Update, ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from openai import OpenAI
import os

# Configuração
BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
ALLOWED_EMAILS = {"drpaulo@gmail.com", "andreia@gmail.com", "samurai@mtc.com"}
AUTHORIZED_USERS = set()

openai_client = OpenAI(api_key="SUA_API_OPENAI")

logging.basicConfig(level=logging.INFO)

# Comando para registrar email
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envie seu email para liberar o acesso.")

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip().lower()
    if email in ALLOWED_EMAILS:
        AUTHORIZED_USERS.add(update.effective_user.id)
        await update.message.reply_text("✅ Acesso liberado. Pergunte o que quiser.")
    else:
        await update.message.reply_text("❌ Email não autorizado. Tente novamente.")

# Comando de mensagem
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in AUTHORIZED_USERS:
        await update.message.reply_text("⚠️ Envie seu email primeiro.")
        return

    user_msg = update.message.text

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_msg}]
    )

    reply = response.choices[0].message.content

    for chunk in reply.split("\n"):
        if chunk.strip():
            await update.message.reply_text(chunk.strip())
            await asyncio.sleep(1)

    await update.message.reply_text("Ossu 🥋")

# Inicialização
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email))
app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=list(AUTHORIZED_USERS)), respond))

app.run_polling()
