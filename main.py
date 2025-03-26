import asyncio
import logging
import nest_asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Configurações
BOT_TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
APP_URL = "https://telegram-wsro.onrender.com"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{APP_URL}{WEBHOOK_PATH}"

# Logger
logging.basicConfig(level=logging.INFO)

# Ativa o suporte a múltiplas execuções de loop
nest_asyncio.apply()

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Olá! Bot ativo com Webhook!")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Você disse: {update.message.text}")

# Função principal
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Cria servidor aiohttp
    async def handler(request):
        data = await request.json()
        await app.update_queue.put(Update.de_json(data, app.bot))
        return web.Response()

    # Set Webhook
    await app.bot.set_webhook(WEBHOOK_URL)
    print("✅ Webhook definido com sucesso!")

    # Servidor aiohttp
    web_app = web.Application()
    web_app.router.add_post(WEBHOOK_PATH, handler)
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 10000)
    await site.start()

    print(f"🚀 Bot rodando no Render com webhook em {WEBHOOK_URL}")
    await app.start()
    await app.updater.start_polling()  # opcional como fallback
    await asyncio.Event().wait()  # mantém rodando

if __name__ == "__main__":
    asyncio.run(main())
