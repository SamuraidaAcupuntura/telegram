import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🔐 Token do seu bot
TOKEN = "7877551847:AAED0zlqMiNgmxC4AIoCJMFSMZmV0evfIXM"

# 📧 Lista de e-mails autorizados
emails_autorizados = [
    "cliente1@email.com",
    "cliente2@email.com",
    "cliente3@email.com"
]

# 💾 Armazena usuários autorizados por ID
usuarios_autorizados = set()

# 🎯 Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Olá! Envie o e-mail da sua compra na Hotmart para liberar o acesso ao dojo 🥋")

# ✅ Verifica se o e-mail é autorizado
async def verificar_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    texto = update.message.text.strip()

    if "@" in texto and "." in texto:
        if texto.lower() in emails_autorizados:
            usuarios_autorizados.add(user_id)
            await update.message.reply_text("✅ Acesso liberado! Pode enviar suas perguntas, guerreiro.")
        else:
            await update.message.reply_text("❌ E-mail não encontrado na lista de compradores.")
    elif user_id in usuarios_autorizados:
        await simular_resposta(update)
    else:
        await update.message.reply_text("⛔ Primeiro envie o e-mail da compra para entrar no dojo.")

# ✍️ Simula digitação com mensagens em partes
async def simular_resposta(update: Update) -> None:
    msg = await update.message.reply_text("Escrevendo...")

    resposta_em_partes = [
        "Você acessou a sabedoria do Samurai da Acupuntura 🐉",
        "Essa jornada é feita de disciplina, energia e verdade.",
        "Sinta-se parte da linhagem.",
        "Caminhe com honra.",
        "Ossu!"
    ]

    texto = ""
    for parte in resposta_em_partes:
        texto += parte + "\n"
        await asyncio.sleep(1.5)
        await msg.edit_text(texto)

# 🚀 Executa o bot
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verificar_email))
    app.run_polling()
