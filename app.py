import os
import socket
import uuid
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- STILI CSS COMUNI ---
STYLE = '''
<style>
    body { font-family: sans-serif; background: #121212; color: #fff; text-align: center; padding: 20px; }
    .card { max-width: 500px; margin: auto; background: #1e1e1e; padding: 30px; border-radius: 15px; border: 1px solid #333; }
    input, textarea { width: 90%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #444; background: #2b2b2b; color: #fff; }
    button { background: #28a745; color: white; border: none; padding: 15px 30px; border-radius: 8px; cursor: pointer; font-weight: bold; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px; }
    .key-box { background: #2b2b2b; padding: 10px; border-radius: 10px; border: 1px solid #444; }
    .key-btn { width: 100%; padding: 15px; background: #333; color: white; border: 1px solid #555; border-radius: 5px; cursor: pointer; font-size: 1.2em; }
    .key-btn:active { background: #007bff; }
    .note-input { width: 80%; font-size: 0.7em; margin-top: 5px; padding: 5px; background: #1a1a1a; border: 1px solid #333; }
</style>
'''

# --- PAGINA 1: INSERIMENTO ---
HTML_INDEX = STYLE + '''
<div class="card">
    <h2>📞 Avvia Chiamata</h2>
    <form action="/chiama" method="POST">
        <input name="numero" placeholder="Inserisci numero (es. +39347...)" required>
        <textarea name="testo" placeholder="Messaggio da leggere..." rows="4"></textarea>
        <button type="submit">REGISTRA E CHIAMA</button>
    </form>
</div>
'''

# --- PAGINA 2: TASTIERINO + CASELLE ---
HTML_KEYPAD = STYLE + '''
<div class="card" style="max-width: 600px;">
    <h2>📟 Chiamata in corso a: {{ numero }}</h2>
    <p>Clicca i tasti per inviare i toni e scrivi nelle caselle per ricordare le funzioni.</p>
    
    <div class="grid">
        {% for k in ['1','2','3','4','5','6','7','8','9','*','0','#'] %}
        <div class="key-box">
            <button class="key-btn" onclick="sendDTMF('{{k}}')">{{k}}</button>
            <input class="note-input" type="text" placeholder="Associa funzione...">
        </div>
        {% endfor %}
    </div>
    <br>
    <a href="/" style="color: #888; text-decoration: none;">← Chiudi e Torna Indietro</a>
</div>

<script>
    function sendDTMF(key) {
        fetch('/dtmf?tasto=' + encodeURIComponent(key));
    }
</script>
'''

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template_string(HTML_INDEX)

@app.route('/chiama', methods=['POST'])
def chiama():
    numero = request.form.get('numero')
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62')

    # Logica invio SIP (INVITE)
    tag = str(uuid.uuid4())[:8]
    sip_msg = f"INVITE sip:{numero}@{target_ip} SIP/2.0\\r\\nVia: SIP/2.0/UDP {target_ip}:5060;branch=z9hG4bK{tag}\\r\\n\\r\\n"
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(sip_msg.encode(), (target_ip, 5060))
        # Reindirizza alla pagina del tastierino passando il numero
        return render_template_string(HTML_KEYPAD, numero=numero)
    except Exception as e:
        return f"Errore: {e}", 500

@app.route('/dtmf')
def dtmf():
    tasto = request.args.get('tasto')
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62')
    info_msg = f"INFO sip:{target_ip} SIP/2.0\\r\\nSignal={tasto}\\r\\nDuration=160\\r\\n\\r\\n"
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(info_msg.encode(), (target_ip, 5060))
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
