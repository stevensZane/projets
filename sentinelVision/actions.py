import pyttsx3
from datetime import datetime
import os
import requests
from alerte_securite import declencher_buzzer, ser
import cv2
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialisation du moteur de synthèse vocale
moteur = pyttsx3.init()

def consigner_passage(nom):
    """Enregistre le nom et l'heure dans un fichier CSV."""
    fichier_log = 'passages.csv'
    existe = os.path.isfile(fichier_log)
    
    with open(fichier_log, 'a+', encoding='utf-8') as f:
        if not existe:
            f.write("Nom, Heure, Date\n")
        
        maintenant = datetime.now()
        heure = maintenant.strftime('%H:%M:%S')
        date = maintenant.strftime('%d-%m-%Y')
        f.write(f"{nom}, {heure}, {date}\n")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


client_groq = Groq(api_key=GROQ_API_KEY)

def generer_rapport_ia(nom, est_autorise, nb_personnes):
    statut = "autorisé" if est_autorise else "non-identifié et potentiellement suspect"
    
    # On donne du style au prompt
    prompt = f"""
    Tu es Sentinel-AI, une intelligence de sécurité haut de gamme.
    CONTEXTE : 
    - Cible : {nom}
    - Statut : {statut}
    - Effectif détecté : {nb_personnes} personne(s)
    
    MISSION : 
    Rédige un rapport flash. 
    Utilise un ton froid, professionnel et technologique. 
    Si la cible est 'INCONNU', souligne l'anomalie de sécurité. 
    Si nb_personnes > 1, mentionne la formation de groupe.
    Évite les formats de liste, fais des phrases fluides.
    """
    
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return f"🛡️ **SENTINEL REPORT**\n\n{completion.choices[0].message.content.strip()}"
    except Exception:
        return f"⚠️ Alerte : {nom} détecté avec {nb_personnes} individu(s)."
    

def alerter(nom, est_autorise=True, frame=None, nb_personnes=1):
    """Gère le son local et l'envoi du rapport Groq sur Telegram."""
    
    # 1. RÉACTION VOCALE (Locale - CPU)
    if est_autorise:
        moteur.say(f"Bonjour {nom}")
        # 2. Arduino (Signal Vert)
        if ser: ser.write(b'V') 
    else:
        # 1. Voix
        moteur.say("Alerte, individu non autorisé")
        # 2. Arduino (Signal Alerte 'A')
        declencher_buzzer()
        
    moteur.runAndWait()

    # 2. REPORTING TELEGRAM (Cloud - Groq)
    # On n'envoie un rapport Telegram QUE pour les intrus pour ne pas saturer le bot
    if not est_autorise:
        # On demande à Groq de rédiger le rapport
        rapport_ia = generer_rapport_ia(nom, est_autorise, nb_personnes)
        
        if frame is not None:
            # Sauvegarde locale du cliché
            if not os.path.exists('intrus'): os.makedirs('intrus')
            date_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            photo_path = f"intrus/alerte_{date_str}.jpg"
            cv2.imwrite(photo_path, frame)
            
            # Envoi à Telegram (Photo + Rapport écrit par Groq)
            try:
                url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
                with open(photo_path, 'rb') as photo:
                    requests.post(url, 
                                  data={'chat_id': CHAT_ID, 'caption': rapport_ia}, 
                                  files={'photo': photo})
            except Exception as e:
                print(f"Erreur envoi Telegram : {e}")