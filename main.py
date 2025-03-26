import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# 🔐 Lista de e-mails autorizados (clientes Hotmart)
AUTHORIZED_EMAILS = {
    "cliente1@email.com",
    "cliente2@email.com",
    "cliente3@email.com"
}

# 🔗 Relaciona ID do usuário com e-mail validado
authorized_users = {}

# 📩 Comando para validar o e-mail
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bem-vindo! Por favor, envie seu e-mail para validar o acesso.")

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip().lower()
    if email in AUTHORIZED_EMAILS:
        authorized_users[update.effective_user.id] = email
        await update.message.reply_text("✅ E-mail validado! Agora você tem acesso ao assistente.")
    else:
        await update.message.reply_text("❌ Este e-mail não está autorizado. Verifique sua compra.")

# 🤖 Comando de conversa (só funciona se e-mail validado)
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in authorized_users:
        await update.message.reply_text("⚠️ Você precisa validar seu e-mail primeiro.")
        return

    pergunta = update.message.text
    resposta = f"💬 Você perguntou: {pergunta}\n(Resposta automática aqui...)"
    await update.message.reply_text(resposta)

# 🧠 Inicializador com webhook limpo
async def main():
    application = ApplicationBuilder().token("SEU_TOKEN_AQUI").build()

    await application.bot.delete_webhook(drop_pending_updates=True)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email))
    application.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=list(authorized_users.keys())), responder))

    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
