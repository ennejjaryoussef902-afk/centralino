import os
from dotenv import load_dotenv
from twilio.rest import Client

# 1. Carica le tue credenziali dal file .env che abbiamo creato prima
load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_NUMBER')
target_number = os.getenv('MY_PHONE_NUMBER')

client = Client(account_sid, auth_token)

try:
    # 2. Creazione e invio del messaggio
    message = client.messages.create(
        body="Ciao! Questo è un messaggio inviato tramite il tuo script Twilio.",
        from_=twilio_number,
        to=target_number
    )

    print("-" * 30)
    print(f"SMS INVIATO CON SUCCESSO!")
    print(f"ID Messaggio: {message.sid}")
    print("-" * 30)

except Exception as e:
    print(f"Errore durante l'invio: {e}")