import os
import socket
import uuid
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Lista Prefissi (Puoi aggiungerne altri qui sotto)
PAESI = [
    ("Italia", "+39"), ("Albania", "+355"), ("Francia", "+33"), 
    ("Germania", "+49"), ("Spagna", "+34"), ("Regno Unito", "+44"),
    ("Svizzera", "+41"), ("USA/Canada", "+1"), ("Romania", "+40"),
    ("Marocco", "+212"), ("Egitto", "+20"), ("Ucraina", "+380")
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Obuz Global SIP</title>
    <style>
        body { font-family: sans-serif; background: #121212; color: white; text-align: center; padding: 20px; }
        .box { max-width: 400px; margin: auto; background: #1e1e1e; padding: 20px; border-radius: 10px; border: 1px solid #333; }
        select, input, textarea { width: 90%; padding: 12px; margin: 10px 0; border-radius: 5px; border: 1px solid #444; background: #2b2b2b; color: white; }
        .btn-call { background: #28a745; color: white; border: none; padding: 15px; width: 95%; border-radius: 5px; font-weight: bold; cursor: pointer; }
        .keypad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 20px; }
        .key { background: #333; padding: 20px; border-radius: 5px; cursor: pointer; border: 1px solid #444; }
        .key:active { background: #007bff; }
    </style>
</head>
<body>
    <div class="box">
        <h2>🌍 Centralino Obuz</h2>
        <form action="/chiama" method="POST">
            <select name="prefisso">
                {% for nazione, codice in paesi %}
                <option value="{{codice}}">{{nazione}} ({{codice}})</option>
                {% endfor %}
            </select>
            <input type="tel" name="numero" placeholder="Numero senza prefisso" required>
            <textarea name="testo" placeholder="Messaggio vocale..."></textarea>
            <button type="submit" class="btn-call">AVVIA CHIAMATA</button>
        </form>

        <hr style="margin: 20px 0; border: 0; border-top: 1px solid #333;">
        
        <h3>Tastierino DTMF</h3>
        <div class="keypad">
            {% for k in ['1','2','3','4','5','6','7','8','9','*','0','#'] %}
            <div class="key" onclick="fetch('/dtmf?tasto={{k}}')">{{k}}</div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template_string(HTML_TEMPLATE, paesi=PAESI)

@app.route('/chiama', methods=['GET', 'POST'])
def chiama():
    # Prende i dati sia da form (POST) che da URL (GET) per evitare errori 405
    numero = request.values.get('numero')
    prefisso = request.values.get('prefisso', '+39')
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62') # Aggiorna questo IP su Render!

    if not numero:
        return "Errore: Inserisci un numero. <a href='/'>Torna indietro</a>", 400

    completo = f"{prefisso}{numero}"
    
    # Costruzione pacchetto SIP minimale
    tag = str(uuid.uuid4())[:8]
    sip_msg = (
        f"INVITE sip:{completo}@{target_ip} SIP/2.0\r\n"
        f"Via: SIP/2.0/UDP {target_ip}:5060;branch=z9hG4bK{tag}\r\n"
        f"From: <sip:render@obuz.com>;tag={tag}\r\n"
        f"To: <sip:{completo}@{target_ip}>\r\n"
        f"Call-ID: {uuid.uuid4()}\r\n"
        f"CSeq: 1 INVITE\r\n\r\n"
    )

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(sip_msg.encode(), (target_ip, 5060))
        return f"<h1>Chiamata a {completo} avviata!</h1><p>Usa il tastierino per interagire.</p><a href='/'>Torna al Pannello</a>"
    except Exception as e:
        return f"Errore Tecnico: {e}", 500

@app.route('/dtmf', methods=['GET', 'POST'])
def dtmf():
    tasto = request.values.get('tasto')
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62')
    
    # Segnale DTMF tramite SIP INFO
    info_msg = (
        f"INFO sip:{target_ip} SIP/2.0\r\n"
        f"Content-Type: application/dtmf-relay\r\n"
        f"\r\nSignal={tasto}\r\nDuration=160"
    )
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(info_msg.encode(), (target_ip, 5060))
        return "OK", 200
    except:
        return "Errore", 500

if __name__ == '__main__':
    # Porta dinamica per Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
