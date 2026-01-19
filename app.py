import os
import requests
from flask import Flask, request

app = Flask(__name__)

# Variabili salvate su Render (Environment Variables)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

@app.route('/chiama', methods=['POST'])
def handle_github_commit():
    data = request.json
    
    # Estraiamo i dati che mi hai appena mostrato
    commit_msg = data.get('message', 'Nuovo Commit')
    commit_id = data.get('id', 'N/A')[:7] # Primi 7 caratteri dell'ID
    
    text = f"🔔 commit su GitHub!\n📝 Messaggio: {commit_msg}\n🆔 ID: {commit_id}"
    
    # Invio notifica sonora a Telegram
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "disable_notification": False # Farà suonare il telefono
    }
    
    requests.post(url, json=payload)
    return "Notifica inviata", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)