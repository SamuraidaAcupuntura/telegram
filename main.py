import os
import json
import logging
import openai
import base64
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    MessageHandler, CommandHandler, filters
)

# CONFIGURAÇÃO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Carrega lista de usuários autorizados
ARQUIVO_USUARIOS = "usuarios_autorizados.json"

def carregar_usuarios():
    try:
        with open(ARQUIVO_USUARIOS, "r") as f:
            return json.load(f)
    except:
        return {"autorizados": [], "liberados": []}

def salvar_usuarios(data):
    with open(ARQUIVO_USUARIOS, "w") as f:
        json.dump(data, f, indent=2)

# Comando /acesso
async def acesso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔒 Para acessar o Dojo, informe o e-mail usado na compra.")

    return

# Verificação de e-mail
async def verificar_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type != "private":
        return

    user_id = str(update.effective_user.id)
    email = update.message.text.strip().lower()
    usuarios = carregar_usuarios()

    if email in usuarios["autorizados"]:
        if user_id not in usuarios["liberados"]:
            usuarios["liberados"].append(user_id)
            salvar_usuarios(usuarios)
        await update.message.reply_text("✅ Acesso ao Dojo liberado. Envie sua dúvida ou imagem quando desejar.")
    elif "@" in email:
        await update.message.reply_text("❌ Este e-mail não está autorizado. Verifique se usou o mesmo da compra.")

# Handler principal
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    usuarios = carregar_usuarios()

    # Somente libera mensagem se estiver autorizado
    if user_id not in usuarios["liberados"]:
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
                    {"role": "system", "content": "Você é o mentor da Jornada do Samurai. Responda com compaixão e sabedoria."},
                    {"role": "user", "content": [
                        {"type": "text", "text": "Analise esta imagem de forma simbólica e energética."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]}
                ],
                max_tokens=600
            )
        else:
            user_input = update.message.text
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": "Você é o assistente da Jornada do Samurai. Responda com clareza e compaixão."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=600
            )
        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Erro: {e}")
        await update.message.reply_text("⚠️ O Caminho encontrou um obstáculo. Tente novamente em breve.")

# /samurai no grupo
async def comando_samurai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat.type in ["group", "supergroup"]:
        await update.message.reply_text(
            "⚔️ Para iniciar sua Jornada no privado, clique aqui:\n"
            "👉 https://t.me/samurai_da_acupuntura_bot"
        )

# INICIAR
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("acesso", acesso))
    app.add_handler(CommandHandler("samurai", comando_samurai))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_email))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    app.run_polling()
