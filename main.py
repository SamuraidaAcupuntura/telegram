async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message.chat.type != "private":
            return  # Ignora grupos

        user_input = update.message.text
        logger.info(f"Mensagem recebida: {user_input}")
        await update.message.reply_text("Escrevendo...")

        # Cria thread
        thread = await client.beta.threads.create()
        await client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input
        )

        # Executa assistant
        run = await client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        while True:
            status = await client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if status.status == "completed":
                break
            await asyncio.sleep(1)

        # Resposta do assistant
        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        resposta = messages.data[0].content[0].text.value

        # Envia linha por linha
        for linha in resposta.strip().split("\n"):
            if linha.strip():
                await update.message.reply_text(linha.strip())
                await asyncio.sleep(0.4)  # pausa curta para simular "fala"

        # Encerra com Ossu
        await update.message.reply_text("Ossu.")

    except Exception as e:
        logger.error("Erro ao responder:", exc_info=e)
        try:
            await update.message.reply_text("Algo deu errado no dojo. Tente novamente.")
        except:
            pass
