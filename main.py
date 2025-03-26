import logging
import time
from telegram import Update, ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

# Token do bot já configurado
BOT_TOKEN = '7877551847:AAED0zlqMiNgmxC4AIoCJMFSMZmV0evfIXM'

# E-mails autorizados
emails_autorizados = [
    "cliente1@email.com",
    "cliente2@email.com",
    "samurai@acupuntura.com",
    "andreia@divergente.com"
]

# Mapeia o user_id com o e-mail validado
usuarios_autenticados = {}

# Log
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Início do bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bem-vindo ao assistente do Samurai 🥋\nDigite seu e-mail para validar seu acesso:")

# Resposta geral
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    texto = update.message.text.strip().lower()

    if user_id not in usuarios_autenticados:
        if texto in emails_autorizados:
            usuarios_autenticados[user_id] = texto
            await update.message.reply_text("✅ E-mail validado com sucesso! Pode enviar sua pergunta agora.")
        else:
            await update.message.reply_text("❌ E-mail não autorizado. Por favor, tente novamente.")
        return

    # Se já validado, simula digitação e responde
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    time.sleep(2)

    await update.message.reply_text("Estou analisando sua pergunta...")
    time.sleep(2)

    resposta = (
        "Essa é uma resposta simbólica do assistente Samurai.\n"
        "Em breve estarei conectado à inteligência total do Caminho.\n\n"
        "Ossu 🥋"
    )
    await update.message.reply_text(resposta)

# App e handlers
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

app.run_polling()
