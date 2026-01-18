# 📞 Centralino VoIP Automatizzato (Zero-Cost & No-Password)

Sistema di notifica vocale basato su **Asterisk** e **Kali Linux (WSL)**. Il sistema monitora i commit di GitHub e fa squillare il tuo smartphone su **Zoiper**, portandoti istantaneamente in una stanza audio senza richiedere password.

## 🚀 Funzionamento
1. **GitHub Trigger**: Un nuovo commit sul branch `main`.
2. **Pipedream**: Filtra l'evento e invia un segnale HTTP POST.
3. **Ngrok Tunnel**: Trasmette il segnale dall'esterno al tuo PC locale.
4. **Python Bridge**: Riceve il segnale e comanda il centralino.
5. **Asterisk (Docker)**: Effettua la chiamata verso l'interno `6001`.
6. **Zoiper**: Ricevi la chiamata e sei in stanza audio (No Password).

---

## 🛠️ Configurazione del Centralino (Docker)

Assicurati che il contenitore sia attivo:
```bash
sudo docker start mio-centralino
