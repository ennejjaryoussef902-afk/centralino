import os
import socket
import uuid
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- STILE CSS ---
STYLE = '''
<style>
    body { font-family: 'Segoe UI', sans-serif; background: #121212; color: #fff; text-align: center; padding: 20px; }
    .card { max-width: 500px; margin: auto; background: #1e1e1e; padding: 25px; border-radius: 15px; border: 1px solid #333; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    .row { display: flex; justify-content: center; gap: 10px; margin-bottom: 10px; }
    .prefisso { width: 80px; padding: 12px; border-radius: 8px; border: 1px solid #444; background: #2b2b2b; color: #00ff00; font-weight: bold; text-align: center; }
    .numero { flex-grow: 1; padding: 12px; border-radius: 8px; border: 1px solid #444; background: #2b2b2b; color: #fff; }
    textarea { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #444; background: #2b2b2b; color: #fff; box-sizing: border-box; }
    .btn-call { background: #28a745; color: white; border: none; padding: 15px 30px; border-radius: 8px; cursor: pointer; font-weight: bold; width: 100%; font-size: 16px; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 20px; }
    .key-box { background: #2b2b2b; padding: 10px; border-radius: 10px; border: 1px solid #444; }
    .key-btn { width: 100%; padding: 15px; background: #333; color: white; border: 1px solid #555; border-radius: 8px; cursor: pointer; font-size: 1.5em; transition: 0.2s; }
    .key-btn:active { background: #007bff; transform: scale(0.9); }
    .note-input { width: 90%; font-size: 11px; margin-top: 8px; padding: 5px; background: #111; border: 1px solid #444; color: #aaa; border-radius: 4px; }
</style>
'''

# --- PAGINA 1: INPUT ---
HTML_INDEX = STYLE + '''
<div class="card">
    <h2>📞 Avvia Chiamata</h2>
    <form action="/chiama" method="POST">
        <div class="row">
            <input name="prefisso" class="prefisso" value="+39" placeholder="+39">
            <input name="numero" class="numero" placeholder="Numero di telefono" required>
        </div>
        <textarea name="testo" placeholder="Messaggio vocale da trasmettere..." rows="3"></textarea>
        <button type="submit" class="btn-call">REGISTRA E CHIAMA</button>
    </form>
</div>
'''

# --- PAGINA 2: TASTIERINO ---
HTML_KEYPAD = STYLE + '''
<div class="card" style="max-width: 550px;">
    <h3>In chiamata con: <span style="color:#00ff00;">{{ completo }}</span></h3>
    <div class="grid">
        {% for k in ['1','2','3','4','5','6','7','8','9','*','0','#'] %}
        <div class="key-box">
            <button class="key-btn" onclick="sendDTMF('{{k}}')">{{k}}</button>
            <input class="note-input" type="text" placeholder="Cosa fa il tasto {{k}}?">
        </div>
        {% endfor %}
    </div>
    <br>
    <a href="/" style="color: #666; text-decoration: none;">← Termina e Torna Indietro</a>
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
    prefisso = request.form.get('prefisso', '+39')
    numero = request.form.get('numero')
    completo = f"{prefisso}{numero}"
    
    # Risoluzione IP per evitare Errno -2
    target_ip = os.environ.get('SIP_TARGET', '').strip()
    if not target_ip:
        return "Errore: SIP_TARGET non configurato su Render!", 500

    # Invio SIP minimale
    sip_msg = f"INVITE sip:{completo}@{target_ip} SIP/2.0\r\n\r\n"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(2)
            s.sendto(sip_msg.encode(), (target_ip, 5060))
        return render_template_string(HTML_KEYPAD, completo=completo)
    except Exception as e:
        return f"Errore Connessione (Errno -2): {e}", 500

@app.route('/dtmf')
def dtmf():
    tasto = request.args.get('tasto')
    target_ip = os.environ.get('SIP_TARGET', '').strip()
    msg = f"INFO sip:{target_ip} SIP/2.0\r\nSignal={tasto}\r\n\r\n"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(msg.encode(), (target_ip, 5060))
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
