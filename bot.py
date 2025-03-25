import os
import logging
import openai
import requests
from io import BytesIO
from PIL import Image
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 📌 Sua API KEY da OpenAI
openai.api_key = "SUA_OPENAI_API_KEY_AQUI"

# 📌 Lista de IDs autorizados (você pode adicionar ou remover)
ALUNOS_AUTORIZADOS = [
    5254297,  # Substitua pelo seu ID real
]

# 🎯 Início do Bot
logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALUNOS_AUTORIZADOS:
        await update.message.reply_text("❌ Acesso negado. Você não está autorizado.")
        return
    await update.message.reply_text("🥋 Bem-vindo ao Assistente da Jornada do Samurai!\nEnvie uma pergunta ou uma imagem para análise.")

async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALUNOS_AUTORIZADOS:
        await update.message.reply_text("❌ Acesso negado.")
        return
    prompt = update.message.text
    await update.message.reply_text("🧠 Samurai está refletindo...")

    try:
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Você é um mestre de Medicina Tradicional Chinesa."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao responder: {e}")

async def imagem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALUNOS_AUTORIZADOS:
        await update.message.reply_text("❌ Acesso negado.")
        return
    await update.message.reply_text("🖼️ Imagem recebida. Analisando...")

    photo = await update.message.photo[-1].get_file()
    image_bytes = requests.get(photo.file_path).content

    try:
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Descreva a imagem e sugira algo relacionado à Medicina Chinesa."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{BytesIO(image_bytes).getvalue().hex()}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(f"❌ Erro ao processar imagem: {e}")

def main():
    app = ApplicationBuilder().token("SEU_BOT_TOKEN_DO_TELEGRAM").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto))
    app.add_handler(MessageHandler(filters.PHOTO, imagem))

    print("🚀 Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    main()
