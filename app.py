import os
from flask import Flask, request, render_template_string
import socket

app = Flask(__name__)

# Interfaccia grafica semplice
HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Centralino Obuz</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding-top: 50px; background: #f4f4f4; }
        .card { background: white; padding: 20px; border-radius: 10px; display: inline-block; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        input { padding: 10px; width: 200px; border: 1px solid #ccc; border-radius: 5px; }
        button { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #218838; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📞 Chiama da MicroSIP</h2>
        <form action="/chiama" method="post">
            <input type="text" name="numero" placeholder="Inserisci numero (es. 351...)" required>
            <button type="submit">Avvia Chiamata</button>
        </form>
        <p style="font-size: 0.8em; color: #666;">Destinazione: {{ target_ip }}</p>
    </div>
</body>
</html>
'''

def invia_pacchetto_sip(target_ip, numero_da_chiamare):
    # Messaggio SIP per far comparire il numero su MicroSIP
    sip_msg = (
        f"INVITE sip:{numero_da_chiamare}@{target_ip} SIP/2.0\r\n"
        f"Via: SIP/2.0/UDP render.com:5060;branch=z9hG4bK{os.urandom(4).hex()}\r\n"
        f"From: <sip:centralino@render.com>;tag={os.urandom(4).hex()}\r\n"
        f"To: <sip:{numero_da_chiamare}@{target_ip}>\r\n"
        f"Call-ID: {os.urandom(16).hex()}\r\n"
        f"CSeq: 1 INVITE\r\n"
        f"Contact: <sip:centralino@render.com>\r\n"
        f"Content-Type: application/sdp\r\n"
        f"Content-Length: 0\r\n\r\n"
    )
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(sip_msg.encode(), (target_ip, 5060))

@app.route('/')
def index():
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62').split('@')[-1]
    return render_template_string(HTML_PAGE, target_ip=target_ip)

@app.route('/chiama', methods=['POST'])
def chiama():
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62').split('@')[-1]
    numero = request.form.get('numero')
    print(f"Comando ricevuto: Chiamare {numero} su {target_ip}")
    invia_pacchetto_sip(target_ip, numero)
    return f"<h3>Chiamata verso {numero} inviata a MicroSIP!</h3><a href='/'>Torna indietro</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
