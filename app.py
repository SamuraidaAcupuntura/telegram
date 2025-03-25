from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

EMAILS_FILE = 'emails.json'

# 📨 Carrega os e-mails autorizados
def carregar_emails():
    if not os.path.exists(EMAILS_FILE):
        with open(EMAILS_FILE, 'w') as f:
            json.dump([], f)
    with open(EMAILS_FILE, 'r') as f:
        return json.load(f)

# 💾 Salva e-mails novos
def salvar_emails(emails):
    with open(EMAILS_FILE, 'w') as f:
        json.dump(emails, f, indent=2)

# 🔗 Endpoint da Hotmart
@app.route('/hotmart-webhook', methods=['POST'])
def hotmart_webhook():
    data = request.json
    email = data.get('buyer', {}).get('email') or data.get('data', {}).get('buyer_email')

    if not email:
        return jsonify({'status': 'erro', 'mensagem': 'E-mail não encontrado no payload'}), 400

    emails = carregar_emails()
    if email not in emails:
        emails.append(email)
        salvar_emails(emails)

    return jsonify({'status': 'ok', 'email': email}), 200

# 🔐 Verifica se o e-mail está autorizado
@app.route('/verificar-email', methods=['POST'])
def verificar_email():
    data = request.json
    email = data.get('email')

    emails = carregar_emails()
    if email in emails:
        return jsonify({'autorizado': True})
    else:
        return jsonify({'autorizado': False})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
