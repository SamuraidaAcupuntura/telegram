import os
import openai
import requests
from flask import Flask, request
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# Configurações
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ALLOWED_EMAILS = [
    'paulocosta@samuraidaacupuntura.com.br',
    'alceuacosta@gmail.com',
    'andreiabioterapia@hotmail.com'
]

openai.api_key = OPENAI_API_KEY
app = Flask(__name__)

# Função de análise de imagem via GPT
async def process_image_and_text(image_url, text):
    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text or "Descreva a imagem."},
                    {"type": "image_url", "image_url": {"url": image_url}}
                ]
            }
        ],
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

# Função de resposta no Telegram
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo = update.message.photo[-1]
        photo_file = await photo.get_file()
        image_url = photo_file.file_path
        prompt = update.message.caption or "O que há nesta imagem?"
        await update.message.reply_text("🧠 Samurai está analisando a imagem...")

        try:
            result = await process_image_and_text(image_url, prompt)
            await update.message.reply_text(result)
        except Exception as e:
            await update.message.reply_text(f"⚠️ Erro: {e}")
    else:
        await update.message.reply_text("Envie uma imagem com uma pergunta ou legenda!")

# Inicialização do bot
@app.route('/')
def home():
    return "Bot Samurai rodando com GPT-4 Vision!"

async def start_bot():
    app_telegram = ApplicationBuilder().token(BOT_TOKEN).build()
    app_telegram.add_handler(MessageHandler(filters.ALL, handle_message))
    await app_telegram.initialize()
    await app_telegram.start()
    print("🤖 Bot iniciado.")
    await app_telegram.updater.start_polling()
    await app_telegram.updater.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(start_bot())
