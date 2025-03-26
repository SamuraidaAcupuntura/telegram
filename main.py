import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import openai

# 🔒 Credenciais e e-mails permitidos
BOT_TOKEN = '7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80'
OPENAI_API_KEY = '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'
EMAILS_AUTORIZADOS = ['paulocosta@samuraidaacupuntura.com.br', 'andreiabioterapia@hotmail.com']

openai.api_key = OPENAI_API_KEY
usuarios_autorizados = set()

# Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 🥋 Comandos do Bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Envie seu e-mail para ativar o acesso, guerreiro.")

async def verificar_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip().lower()
    if email in EMAILS_AUTORIZADOS:
        usuarios_autorizados.add(update.effective_user.id)
        await update.message.reply_text("✅ Acesso concedido. Pode perguntar, guerreiro.")
    else:
        await update.message.reply_text("❌ E-mail não autorizado. Tente novamente.")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in usuarios_autorizados:
        await update.message.reply_text("⚠️ Envie seu e-mail para liberar o acesso.")
        return

    pergunta = update.message.text
    await update.message.chat.send_action(action="typing")

    try:
        resposta = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": pergunta}]
        )
        texto_resposta = resposta.choices[0].message.content

        frases = texto_resposta.split(". ")
        for frase in frases:
            if frase.strip():
                await update.message.chat.send_action(action="typing")
                await asyncio.sleep(1.5)  # Delay entre frases
                await update.message.reply_text(frase.strip() + ".")
        
        await asyncio.sleep(1)
        await update.message.reply_text("Ossu 🥋")

    except Exception as e:
        logger.error(f"Erro ao consultar OpenAI: {e}")
        await update.message.reply_text("❌ Erro ao buscar resposta. Tente novamente.")

# 🧠 Execução
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_email))
    app.add_handler(MessageHandler(filters.TEXT & filters.User(user_id=usuarios_autorizados), responder))

    print("🔥 Bot rodando com delay e estilo Samurai...")
    app.run_polling()
