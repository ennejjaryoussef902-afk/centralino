import os
import socket
import uuid
from flask import Flask, request, render_template_string
from gtts import gTTS

app = Flask(__name__)

HTML_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Obuz Control Panel</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #1a1a1a; color: white; text-align: center; padding: 20px; }
        .container { max-width: 400px; margin: auto; background: #2d2d2d; padding: 20px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        input, textarea { width: 90%; padding: 12px; margin: 10px 0; border-radius: 8px; border: none; font-size: 16px; }
        .call-btn { width: 100%; background: #28a745; color: white; padding: 15px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 18px; }
        
        .keypad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 30px; padding: 10px; }
        .key { background: #444; padding: 20px; border-radius: 50%; width: 60px; height: 60px; line-height: 60px; margin: auto; cursor: pointer; font-size: 20px; transition: 0.2s; user-select: none; border: 1px solid #555; }
        .key:hover { background: #555; }
        .key:active { background: #007bff; transform: scale(0.9); }
        h3 { color: #888; font-size: 14px; text-transform: uppercase; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>📞 Avvia Chiamata</h2>
        <form action="/chiama" method="POST">
            <input name="numero" placeholder="+39 3XX XXX XXXX" required>
            <textarea name="messaggio" placeholder="Cosa devo dire?"></textarea>
            <button type="submit" class="call-btn">CHIAMA ORA</button>
        </form>

        <h3>Comandi in Chiamata (DTMF)</h3>
        <div class="keypad">
            {% for i in ['1','2','3','4','5','6','7','8','9','*','0','#'] %}
            <div class="key" onclick="sendDTMF('{{i}}')">{{i}}</div>
            {% endfor %}
        </div>
    </div>

    <script>
        function sendDTMF(tasto) {
            console.log("Invio tono: " + tasto);
            fetch('/dtmf?tasto=' + tasto);
        }
    </script>
</body>
</html>
'''

# [Resto della logica genera_pacchetto_sip, /chiama e /dtmf come prima]
# ... (assicurati di mantenere le funzioni Python del messaggio precedente)
