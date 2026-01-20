import os
import socket
from flask import Flask, request, render_template_string

app = Flask(__name__)

# --- LAYOUT FISSO (Non cambierà più) ---
STYLE = '''
<style>
    body { font-family: sans-serif; background: #121212; color: white; text-align: center; padding: 20px; }
    .container { max-width: 500px; margin: auto; background: #1e1e1e; padding: 25px; border-radius: 15px; border: 1px solid #333; }
    .phone-row { display: flex; gap: 10px; justify-content: center; margin-bottom: 15px; }
    .pref { width: 75px; padding: 12px; border-radius: 8px; border: 1px solid #444; background: #2b2b2b; color: #00ff00; text-align: center; font-weight: bold; font-size: 1.1em; }
    .num { flex-grow: 1; padding: 12px; border-radius: 8px; border: 1px solid #444; background: #2b2b2b; color: white; font-size: 1.1em; }
    .btn-main { width: 100%; background: #28a745; color: white; padding: 15px; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
    .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 20px; }
    .key-box { background: #252525; padding: 10px; border-radius: 8px; border: 1px solid #333; }
    .key-btn { width: 100%; padding: 15px; background: #333; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1.5em; }
    .note { width: 95%; margin-top: 5px; font-size: 11px; background: #111; color: #00ff00; border: 1px solid #444; padding: 5px; text-align: center; }
</style>
'''

@app.route('/')
def index():
    # Prende il prefisso predefinito dalle variabili di Render (es. +39)
    default_pref = os.environ.get('DEFAULT_PREF', '+39')
    return render_template_string(STYLE + '''
    <div class="container">
        <h2>📞 Invio Rapido</h2>
        <form action="/chiama" method="POST">
            <div class="phone-row">
                <input name="prefisso" class="pref" value="{{ p }}">
                <input name="numero" class="num" placeholder="Numero" required autofocus>
            </div>
            <textarea name="testo" style="width:100%; background:#2b2b2b; color:white; border-radius:8px; padding:10px;" placeholder="Messaggio..."></textarea>
            <button type="submit" class="btn-main">CHIAMA E APRI TASTIERINO</button>
        </form>
    </div>
    ''', p=default_pref)

@app.route('/chiama', methods=['POST'])
def chiama():
    pref = request.form.get('prefisso', '+39')
    num = request.form.get('numero', '')
    completo = f"{pref}{num}"
    target_ip = os.environ.get('SIP_TARGET', '').strip()

    # Invio SIP (UDP)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(f"INVITE sip:{completo}@{target_ip} SIP/2.0\r\n\r\n".encode(), (target_ip, 5060))
        
        return render_template_string(STYLE + '''
        <div class="container">
            <h3>Tastierino per: {{ c }}</h3>
            <div class="grid">
                {% for k in ['1','2','3','4','5','6','7','8','9','*','0','#'] %}
                <div class="key-box">
                    <button class="key-btn" onclick="fetch('/dtmf?tasto={{k}}')">{{k}}</button>
                    <input class="note" placeholder="Associa...">
                </div>
                {% endfor %}
            </div>
            <br><a href="/" style="color:#888; text-decoration:none;">← Nuova Chiamata</a>
        </div>
        ''', c=completo)
    except Exception as e:
        return f"Errore: {e}", 500

@app.route('/dtmf')
def dtmf():
    tasto = request.args.get('tasto')
    target_ip = os.environ.get('SIP_TARGET', '').strip()
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(f"INFO sip:{target_ip} SIP/2.0\r\nSignal={tasto}\r\n\r\n".encode(), (target_ip, 5060))
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
