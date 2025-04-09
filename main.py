import os
import httpx
import json
import asyncio
from flask import Flask, request

from threading import Thread
from time import sleep

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

openai_headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta": "assistants=v2",
    "Content-Type": "application/json",
}

def send_telegram_message(chat_id, text):
    httpx.post(f"{TELEGRAM_API_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def responder_em_blocos(chat_id, texto):
    partes = texto.split("\n\n")
    for parte in partes:
        if parte.strip():
            send_telegram_message(chat_id, parte.strip())
            sleep(1.2)
    send_telegram_message(chat_id, "Ossu")

@app.route("/", methods=["POST"])
def webhook():
    data = request.json
    chat = data.get("message", {}).get("chat", {})
    if chat.get("type") != "private":
        return {"ok": True}

    chat_id = chat["id"]
    user_msg = data["message"].get("text", "")
    caption = data["message"].get("caption", "")
    content = user_msg or caption
    image_url = None

    photo_list = data["message"].get("photo")
    if photo_list:
        file_id = photo_list[-1]["file_id"]
        file_info = httpx.get(f"{TELEGRAM_API_URL}/getFile?file_id={file_id}").json()
        file_path = file_info["result"]["file_path"]
        image_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"

    try:
        thread_response = httpx.post("https://api.openai.com/v1/threads", headers=openai_headers)
        thread_id = thread_response.json()["id"]

        msg_payload = {"role": "user", "content": content}
        if image_url:
            msg_payload["attachments"] = [{"type": "image_url", "image_url": {"url": image_url}}]

        httpx.post(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=openai_headers,
            json=msg_payload
        )

        run_response = httpx.post(
            f"https://api.openai.com/v1/threads/{thread_id}/runs",
            headers=openai_headers,
            json={"assistant_id": ASSISTANT_ID}
        )
        run_id = run_response.json()["id"]

        while True:
            status_response = httpx.get(
                f"https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}",
                headers=openai_headers
            ).json()
            if status_response["status"] == "completed":
                break
            sleep(1)

        messages = httpx.get(
            f"https://api.openai.com/v1/threads/{thread_id}/messages",
            headers=openai_headers
        ).json()

        final_answer = messages["data"][0]["content"][0]["text"]["value"]
        Thread(target=responder_em_blocos, args=(chat_id, final_answer)).start()

    except Exception as e:
        print("Erro:", e)
        send_telegram_message(chat_id, "⚠️ Ocorreu um erro. Tente novamente.")

    return {"ok": True}

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
