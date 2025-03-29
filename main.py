import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
assistant_id = os.getenv("ASSISTANT_ID")

if not api_key or not assistant_id:
    raise ValueError("Variáveis de ambiente ausentes.")

headers = {
    "Authorization": f"Bearer {api_key}",
    "OpenAI-Beta": "assistants=v2",
    "Content-Type": "application/json",
}

try:
    # 1. Criar thread
    response = httpx.post("https://api.openai.com/v1/threads", headers=headers)
    response.raise_for_status()
    thread_id = response.json()["id"]
    print("✅ Thread criada:", thread_id)

    # 2. Enviar mensagem para o thread
    message_payload = {
        "role": "user",
        "content": "Olá, tudo bem?"
    }
    response = httpx.post(
        f"https://api.openai.com/v1/threads/{thread_id}/messages",
        headers=headers,
        json=message_payload
    )
    response.raise_for_status()
    print("✅ Mensagem enviada")

    # 3. Iniciar execução com o assistant_id
    run_payload = {
        "assistant_id": assistant_id
    }
    response = httpx.post(
        f"https://api.openai.com/v1/threads/{thread_id}/runs",
        headers=headers,
        json=run_payload
    )
    response.raise_for_status()
    print("✅ Execução iniciada:", response.json()["id"])

except httpx.HTTPStatusError as e:
    print("❌ Erro HTTP:", e.response.status_code, e.response.text)
except Exception as e:
    print("❌ Erro:", str(e))
