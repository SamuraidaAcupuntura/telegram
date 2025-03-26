import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI

# SEUS DADOS
BOT_TOKEN = "7877551847:AAED0zlqMiNgmxC4AIoCJMFSMZmV0evfIXM"
OPENAI_API_KEY = "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"
APP_URL = "https://telegram-wsro.onrender.com"

# Inicializa o cliente OpenAI com sua chave
client = OpenAI(api_key=OPENAI_API_KEY)

# Configura logs
logging.basicConfig(level=logging.INFO)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Sou o assistente do Samurai da Acupuntura. Me envie uma pergunta.")

# Mensagens comuns
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.chat.send_action(action="typing")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é o assistente do Samurai da Acupuntura. Responda com sabedoria, empatia e profundidade."},
                {"role": "user", "content": user_message}
            ]
        )
        resposta = response.choices[0].message.content
        await update.message.reply_text(resposta)
    except Exception as e:
        logging.error(f"Erro ao buscar resposta: {e}")
        await update.message.reply_text("Ocorreu um erro ao buscar a resposta. Tente novamente mais tarde.")

# Função principal
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    await app.bot.set_webhook(url=f"{APP_URL}/webhook")
    logging.info("Webhook definido com sucesso!")

    await app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_path="/webhook"
    )

# Executa o bot
if __name__ == "__main__":
    asyncio.run(main())
