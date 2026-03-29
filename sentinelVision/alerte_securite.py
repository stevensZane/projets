import serial
import time

try:
    ser = serial.Serial('COM9', 9600, timeout=1)
    time.sleep(2) # Pause pour laisser l'Arduino s'initialiser
    print("✅ Arduino connecté avec succès")
except:
    print("❌ Arduino non trouvé sur le port spécifié")
    ser = None

def declencher_buzzer():
    if ser:
        ser.write(b'A')
        print(">>> [PHYSIQUE] Signal envoyé à l'Arduino : ALARME !")
    else:
        # Simulation quand la carte n'est pas branchée
        print(">>> [SIMULATION] BIP! BIP! BIP! (L'Arduino aurait sonné ici)")