import os
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from openai import AsyncOpenAI
import asyncio

TOKEN = "7877551847:AAGEWNbIXmg49m4MJp8IPDycahowEi7TU80"
WEBHOOK_URL = "https://telegram-wsro.onrender.com"
OPENAI_API_KEY = "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"

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text
    chat_id = update.effective_chat.id

    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        resposta = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um mestre samurai espiritual, calmo, sábio e gentil. Fale como um mentor sereno, e termine suas respostas com 'ossu.'"},
                {"role": "user", "content": texto}
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        conteudo = resposta.choices[0].message.content.strip()
        await context.bot.send_message(chat_id=chat_id, text=conteudo + "\n\nossu.")

    except Exception as e:
        print(f"[ERRO AO RESPONDER]: {e}")
        await context.bot.send_message(chat_id=chat_id, text="⚠️ Tive um problema interno ao responder. Verifique sua chave da OpenAI ou o modelo. \nossu.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 10000)),
        webhook_url=WEBHOOK_URL
    )
