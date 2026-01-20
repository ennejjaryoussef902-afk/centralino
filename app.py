import os
import socket
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Lista estesa dei prefissi (puoi aggiungerne altri facilmente)
PAESI = [
    ("Italia", "+39"), ("Albania", "+355"), ("Argentina", "+54"), ("Austria", "+43"),
    ("Belgio", "+32"), ("Brasile", "+55"), ("Canada", "+1"), ("Cina", "+86"),
    ("Egitto", "+20"), ("Francia", "+33"), ("Germania", "+49"), ("Giappone", "+81"),
    ("Grecia", "+30"), ("India", "+91"), ("Marocco", "+212"), ("Olanda", "+31"),
    ("Portogallo", "+351"), ("Regno Unito", "+44"), ("Romania", "+40"), ("Russia", "+7"),
    ("Spagna", "+34"), ("Stati Uniti", "+1"), ("Svizzera", "+41"), ("Tunisia", "+216"),
    ("Turchia", "+90"), ("Ucraina", "+380")
]

HTML = '''
<!DOCTYPE html>
<html style="background:#1a1a1a; color:#e0e0e0; font-family:sans-serif; text-align:center;">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        select, input, textarea { width: 80%; max-width: 300px; padding: 12px; margin: 10px 0; border-radius: 5px; border: 1px solid #333; background: #222; color: white; }
        .btn-call { background: #28a745; color: white; font-weight: bold; border: none; padding: 15px 30px; cursor: pointer; border-radius: 5px; }
        .keypad { display: grid; grid-template-columns: repeat(3, 70px); gap: 10px; justify-content: center; margin-top: 20px; }
        .key { background: #333; border: 1px solid #444; color: white; padding: 20px; font-size: 18px; border-radius: 5px; cursor: pointer; }
        .key:active { background: #007bff; }
    </style>
</head>
<body>
    <h1>🌍 Centralino Mondiale</h1>
    
    <form action="/chiama" method="POST">
        <select name="prefisso">
            {% for nazione, codice in paesi %}
            <option value="{{codice}}">{{nazione}} ({{codice}})</option>
            {% endfor %}
        </select><br>
        <input name="numero" placeholder="Inserisci numero" type="tel" required><br>
        <textarea name="testo" placeholder="Messaggio da leggere..."></textarea><br>
        <button type="submit" class="btn-call">AVVIA CHIAMATA</button>
    </form>

    <div style="margin-top:40px; border-top: 1px solid #333; padding-top:20px;">
        <h3>Invio Codici Tastierino</h3>
        <div class="keypad">
            {% for k in ['1','2','3','4','5','6','7','8','9','*','0','#'] %}
            <div class="key" onclick="fetch('/dtmf?tasto={{k}}')">{{k}}</div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML, paesi=PAESI)

@app.route('/chiama', methods=['POST'])
def chiama():
    prefisso = request.form.get('prefisso')
    num = request.form.get('numero')
    completo = f"{prefisso}{num}"
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62')

    # Invia il segnale SIP
    msg = f"INVITE sip:{completo}@{target_ip} SIP/2.0\r\n\r\n"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(msg.encode(), (target_ip, 5060))
        return f"<h3>Chiamata partita verso {completo}</h3><p>Usa il tastierino sotto per i codici.</p><a href='/' style='color:#007bff;'>Indietro</a>"
    except Exception as e:
        return f"Errore: {e}", 500

@app.route('/dtmf')
def dtmf():
    tasto = request.args.get('tasto')
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62')
    msg = f"INFO sip:{target_ip} SIP/2.0\r\nSignal={tasto}\r\nDuration=160\r\n\r\n"
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(msg.encode(), (target_ip, 5060))
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
