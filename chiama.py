# Esempio: Chiama l'interno 6001 e mettilo in stanza
import telnetlib

def chiama_e_connetti(interno):
    tn = telnetlib.Telnet("localhost", 5038)
    tn.read_until(b"Asterisk Call Manager")
    tn.write(b"Action: Login\nUsername: admin\nSecret: superpass\n\n")
    tn.write(f"Action: Originate\nChannel: PJSIP/{interno}\nExten: 100\nContext: default\nPriority: 1\n\n".encode())
    tn.write(b"Action: Logoff\n\n")
    print(f"Sto facendo squillare l'interno {interno}...")

chiama_e_connetti("6001")