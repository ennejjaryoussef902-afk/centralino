import os
from flask import Flask, request, render_template_string
from gtts import gTTS # Trasforma il testo in voce
import socket

app = Flask(__name__)

HTML_PAGE = '''
<body style="font-family:sans-serif; text-align:center;">
    <h2>Centralino TwiML Style</h2>
    <form action="/chiama" method="POST">
        <input name="numero" placeholder="Numero (+39...)"><br><br>
        <textarea name="messaggio" placeholder="Cosa devo dire?"></textarea><br><br>
        <button type="submit">Genera Voce e Chiama</button>
    </form>
</body>
'''

@app.route('/chiama', methods=['POST'])
def chiama():
    numero = request.form.get('numero')
    testo = request.form.get('messaggio')
    target_ip = os.environ.get('SIP_TARGET', '37.163.81.62')

    # 1. Genera il file audio dal testo inserito
    tts = gTTS(text=testo, lang='it')
    tts.save("messaggio.mp3")
    
    # 2. Invia segnale a MicroSIP
    invia_segnale_sip(target_ip, numero)
    
    return f"Sto chiamando {numero} per dire: '{testo}'"

def invia_segnale_sip(ip, num):
    # Logica per far squillare MicroSIP sulla porta 5060
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        msg = f"INVITE sip:{num}@{ip} SIP/2.0\r\nContent-Length: 0\r\n\r\n"
        s.sendto(msg.encode(), (ip, 5060))

@app.route('/')
def home(): return HTML_PAGE

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
