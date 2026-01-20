import os
from flask import Flask, request, render_template_string
from gtts import gTTS
import socket

app = Flask(__name__)

# Interfaccia con Tastierino Numerico
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <style>
        .keypad { display: grid; grid-template-columns: repeat(3, 60px); gap: 10px; justify-content: center; margin-top: 20px; }
        .key { padding: 20px; background: #eee; border: 1px solid #ccc; cursor: pointer; text-align: center; font-weight: bold; border-radius: 5px; }
        .key:active { background: #ddd; }
        input, textarea { width: 200px; margin-bottom: 10px; padding: 8px; }
        button#call-btn { background: green; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body style="font-family:sans-serif; text-align:center; padding-top:30px;">
    <h2>Centralino Interattivo</h2>
    <form action="/chiama" method="POST">
        <input name="numero" placeholder="Numero (+39...)" required><br>
        <textarea name="messaggio" placeholder="Messaggio vocale..."></textarea><br>
        <button type="submit" id="call-btn">Avvia Chiamata</button>
    </form>

    <h3>Tastierino (DTMF)</h3>
    <div class="keypad">
        {% for i in ['1','2','3','4','5','6','7','8','9','*','0','#'] %}
        <div class="key" onclick="inviaTono('{{i}}')">{{i}}</div>
        {% endfor %}
    </div>

    <script>
        function inviaTono(tasto) {
            fetch('/dtmf?tasto=' + encodeURIComponent(tasto));
        }
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/chiama', methods=['POST'])
def chiama():
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62')
    numero = request.form.get('numero')
    testo = request.form.get('messaggio', 'Notifica')
    
    # Genera voce
    tts = gTTS(text=testo, lang='it')
    tts.save("/tmp/messaggio.mp3")
    
    # Segnale SIP
    invia_pacchetto(target_ip, f"INVITE sip:{numero}@{target_ip} SIP/2.0\r\n")
    return f"Chiamata a {numero} avviata. <a href='/'>Torna al tastierino</a>"

@app.route('/dtmf')
def dtmf():
    tasto = request.args.get('tasto')
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62')
    # Invia il segnale INFO (DTMF) a MicroSIP
    msg = f"INFO sip:{target_ip} SIP/2.0\r\nSignal={tasto}\r\nDuration=160\r\n"
    invia_pacchetto(target_ip, msg)
    return "OK", 200

def invia_pacchetto(ip, contenuto):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(contenuto.encode(), (ip, 5060))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
