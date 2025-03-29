import os
import logging
import asyncio
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from dotenv import load_dotenv

# 🔁 Carregar variáveis do .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# 🚨 Verificações obrigatórias
if not TELEGRAM_TOKEN or not OPENAI_API_KEY or not OPENAI_ASSISTANT_ID:
    raise ValueError("⚠️ Variáveis de ambiente não encontradas. Verifique seu .env.")

# 📜 Configuração de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✉️ Função de tratamento das mensagens recebidas
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensagem = update.message.text
    logger.info(f"Mensagem recebida: {mensagem}")

    try:
        # Criar thread
        thread_response = await httpx.AsyncClient().post(
            "https://api.openai.com/v1/threads",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        )
        thread_id = thread_response.json()["id"]

        # Enviar mensagem para o thread
        await httpx.AsyncClient().post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"role": "user", "content": mensagem},
        )

        # Iniciar execução
        run_response = await httpx.AsyncClient().post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            json={"assistant_id": OPENAI_ASSISTANT_ID},
        )

        run_id = run_response.json()["id"]

        # Esperar a execução finalizar
        status = "queued"
        while status not in ["completed", "failed"]:
            await asyncio.sleep(1)
            check = await httpx.AsyncClient().get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
            )
            status = check.json()["status"]

        # Pegar resposta
        messages_response = await httpx.AsyncClient().get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        )
        mensagens = messages_response.json()["data"]
        reply = mensagens[0]["content"][0]["text"]["value"]

        await update.message.reply_text(reply)

    except Exception as e:
        logger.error(f"Erro ao gerar resposta: {e}")
        await update.message.reply_text("⚠️ Desculpe, houve um erro ao processar sua mensagem.")

# 🚀 Função principal
async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("Iniciando o bot...")
    await application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/webhook"
    )

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
