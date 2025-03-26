import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from openai import OpenAI

# Configurar o cliente OpenAI com a nova versão da lib (1.x)
openai_client = OpenAI(api_key="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")

# Ativar logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Resposta ao /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Sou o Samurai da Acupuntura. Envie sua pergunta e eu responderei com a sabedoria dos antigos 🈶")

# Resposta a mensagens de texto
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    try:
        # Enviar a mensagem para a OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}],
        )

        reply = response.choices[0].message.content
        await update.message.reply_text(reply)

    except Exception as e:
        logging.error(f"Erro interno: {e}")
        await update.message.reply_text("⚠️ Tive um problema interno ao responder. Verifique a chave da OpenAI ou o modelo.")

# Iniciar bot
if __name__ == '__main__':
    app = ApplicationBuilder().token("7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot rodando como um guerreiro ancestral 🐉")
    app.run_polling()
