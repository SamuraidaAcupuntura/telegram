import os
import httpx
from flask import Flask, request
import json

app = Flask(__name__)

# Variáveis de ambiente (para segurança no Render, coloque na aba Environment)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "samurai")  # opcional

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Headers para a API da OpenAI
openai_headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta": "assistants=v2",
    "Content-Type": "application/json",
}

def send_telegram_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    httpx.post(f"{TELEGRAM_API_URL}/sendMessage", json=payload)

@app.route('/', methods=['POST'])
def webhook():
    data = request.json

    if 'message' not in data:
        return {"ok": True}

    chat_id = data['message']['chat']['id']
    user_msg = data['message'].get('text', '')

    try:
        # Cria thread
        thread_response = httpx.post("https://api.openai.com/v1/threads", headers=openai_headers)
        thread_response.raise_for_status()
        thread_id = thread_response.json()["id"]

        # Envia mensagem do usuário
        httpx.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=openai_headers,
            json={"role": "user", "content": user_msg}
        )

        # Inicia a execução do assistente
        run_response = httpx.post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers=openai_headers,
            json={"assistant_id": ASSISTANT_ID}
        )
        run_id = run_response.json()["id"]

        # Aguarda a conclusão da execução
        while True:
            run_status = httpx.get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                headers=openai_headers
            ).json()
            if run_status["status"] == "completed":
                break

        # Busca a resposta
        messages = httpx.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=openai_headers
        ).json()

        final_answer = messages['data'][0]['content'][0]['text']['value']
        send_telegram_message(chat_id, final_answer)

    except Exception as e:
        print("Erro:", e)
        send_telegram_message(chat_id, "⚠️ Ocorreu um erro. Tente novamente.")

    return {"ok": True}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

