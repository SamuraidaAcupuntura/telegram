import os
import openai
from flask import Flask, request
from telegram import Update, Bot, ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Configurações
BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
OPENAI_API_KEY = "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"
WEBHOOK_URL = "https://telegram-wsro.onrender.com"  # Substitua pelo URL do seu serviço Render

# Inicializações
openai.api_key = OPENAI_API_KEY
app_flask = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()
bot = Bot(BOT_TOKEN)

# Função para simular digitação e enviar por partes
async def send_typing_and_reply(chat_id, full_text):
    parts = full_text.split(". ")
    for i, part in enumerate(parts):
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(1.8)  # Delay para parecer natural
        final_text = part.strip() + ("." if i < len(parts) - 1 else " Ossu!")
        await bot.send_message(chat_id=chat_id, text=final_text)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Seja bem-vindo, guerreiro do caminho. Escreva sua dúvida.")

# Manipulador de mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.effective_chat.id

    # Avisa que está digitando
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    # Geração com OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": (
                    "Você é um assistente espiritual e sábio, treinado pelo Samurai da Acupuntura, "
                    "comunica-se com profundidade e serenidade. Se finalize sempre com 'Ossu!'. "
                    "Os emails para contato são paulocosta@samuraidaacupuntura.com.br e andreiabioterapia@hotmail.com."
                ),
            },
            {"role": "user", "content": user_message},
        ]
    )

    reply_text = response.choices[0].message["content"]
    await send_typing_and_reply(chat_id, reply_text)

# Rota Webhook
@app_flask.post("/webhook")
async def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, bot)
    await telegram_app.process_update(update)
    return "ok"

# Configuração inicial para definir o webhook
async def set_webhook():
    await bot.delete_webhook()
    await bot.set_webhook(url=WEBHOOK_URL)

# Início
if __name__ == "__main__":
    import asyncio
    import threading

    async def run():
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        await set_webhook()

    threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))).start()
    asyncio.run(run())
