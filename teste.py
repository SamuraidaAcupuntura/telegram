import asyncio
from openai import AsyncOpenAI

async def testar_chave():
    client = AsyncOpenAI(api_key="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")

    try:
        resposta = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "teste de chave"}
            ]
        )
        print("✅ CHAVE FUNCIONANDO")
        print("Resposta:", resposta.choices[0].message.content)
    except Exception as e:
        print("❌ ERRO:", e)

asyncio.run(testar_chave())
