import os
import logging
import openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import base64

# Configurar logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Chaves secretas (use variáveis de ambiente no Render)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

# Função para lidar com as mensagens
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name or "buscador"
    chat_id = update.effective_chat.id

    if update.message.text and update.message.text.lower() in ["oi", "olá", "iniciar", "/start"]:
        await update.message.reply_text(
            f"Bem-vindo à sua jornada interior, {user}.\n"
            "Aqui, você caminha ao lado do Samurai.\n\n"
            "Envie uma dúvida, uma reflexão ou até uma imagem. Eu responderei com o espírito do Caminho."
        )
        return

    try:
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            file_path = await file.download_to_drive()
            with open(file_path, "rb") as img:
                base64_img = base64.b64encode(img.read()).decode("utf-8")
            
            response = openai.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {"role": "system", "content": "Você é o assistente da Jornada do Samurai. Responda com profundidade, compaixão e sabedoria."},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Analise essa imagem de forma simbólica e terapêutica, dentro do espírito da Jornada do Samurai."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}},
                    ]}
                ],
                max_tokens=600
            )
        else:
            user_input = update.message.text
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "Você é o assistente da Jornada do Samurai. Responda com profundidade, compaixão e sabedoria."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=600
            )

        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text("O Caminho encontrou um obstáculo. Tente novamente em breve.")

# Executar o bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()
