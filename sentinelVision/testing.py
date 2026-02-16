import cv2
import numpy as np
import face_recognition as face_rec
import pickle
import time
from ultralytics import YOLO
from actions import consigner_passage, alerter

# --- CONFIGURATION ---
MODELE_YOLO = "yolov8n-face.pt"
FICHIER_ENCODAGES = "encodages.pickle"
ANALYSER_CHAQUE_X_FRAMES = 5  # Un peu plus léger pour le CPU
RESIZE_SCALE = 0.5            # 0.5 est plus standard pour le calcul
SEUIL_RECONNAISSANCE = 0.42
COOLDOWN_ALERT = 5

# --- CHARGEMENT ---
modele_yolo = YOLO(MODELE_YOLO)
with open(FICHIER_ENCODAGES, "rb") as f:
    donnees = pickle.load(f)
encodages_connus, noms_connus = donnees["encodages"], donnees["noms"]

# --- INITIALISATION ---
video = cv2.VideoCapture(0)
compteur_frames = 0
dernier_nom_detecte = None
dernier_temps_alerte = 0
visages_sauvegardes = [] # Garde les infos pour l'affichage entre deux analyses

def lancer_surveillance():
    while True:
        succes, frame = video.read()
        if not succes: break

        compteur_frames += 1

        # Analyse seulement toutes les X frames pour la fluidité
        if compteur_frames % ANALYSER_CHAQUE_X_FRAMES == 0:
            visages_sauvegardes = []
            frame_small = cv2.resize(frame, (0, 0), fx=RESIZE_SCALE, fy=RESIZE_SCALE)

            resultats = modele_yolo(frame_small, stream=True, conf=0.5, imgsz=256, verbose=False)

            for r in resultats:
                nb_personnes = len(r.boxes) # COMPTAGE : Pour ton rapport IA
                
                for box in r.boxes:
                    # Coordonnées et mise à l'échelle
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    x1, y1, x2, y2 = [int(v / RESIZE_SCALE) for v in [x1, y1, x2, y2]]
                    
                    # Sécurité des bordures
                    x1, y1 = max(0, x1), max(0, y1)
                    x2, y2 = min(frame.shape[1], x2), min(frame.shape[0], y2)

                    visage_coupe = frame[y1:y2, x1:x2]
                    if visage_coupe.size == 0: continue

                    # --- LE MARTELAGE DE PRÉCISION (CLAHE) ---
                    # On transforme le crop pour aider face_rec
                    gris = cv2.cvtColor(visage_coupe, cv2.COLOR_BGR2GRAY)
                    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                    gris_egalise = clahe.apply(gris)
                    img_rgb = cv2.cvtColor(gris_egalise, cv2.COLOR_GRAY2RGB)

                    # Reconnaissance
                    loc = [(0, img_rgb.shape[1], img_rgb.shape[0], 0)]
                    encodages = face_rec.face_encodings(img_rgb, known_face_locations=loc)

                    nom, couleur, autorise = "INCONNU", (0, 0, 255), False

                    if encodages:
                        dist = face_rec.face_distance(encodages_connus, encodages[0])
                        idx = np.argmin(dist)
                        if dist[idx] < SEUIL_RECONNAISSANCE:
                            nom = noms_connus[idx]
                            couleur = (0, 255, 0)
                            autorise = True

                    visages_sauvegardes.append((x1, y1, x2, y2, nom, couleur))

                    # --- GESTION DES ALERTES ---
                    temps_actuel = time.time()
                    if (nom != dernier_nom_detecte and temps_actuel - dernier_temps_alerte > COOLDOWN_ALERT):
                        consigner_passage(nom)
                        # On envoie le nombre de personnes détectées par YOLO
                        alerter(nom, est_autorise=autorise, frame=frame, nb_personnes=nb_personnes)
                        dernier_nom_detecte, dernier_temps_alerte = nom, temps_actuel

        # Affichage constant (même entre deux analyses)
        for (x1, y1, x2, y2, nom, couleur) in visages_sauvegardes:
            cv2.rectangle(frame, (x1, y1), (x2, y2), couleur, 2)
            cv2.putText(frame, nom, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, couleur, 2)

        cv2.imshow("Sentinel Vision", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"): break

    video.release()
    cv2.destroyAllWindows()