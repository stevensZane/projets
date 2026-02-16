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
ANALYSER_CHAQUE_X_FRAMES = 3 
RESIZE_SCALE = 0.5
SEUIL_RECONNAISSANCE = 0.42

# --- PARAMÈTRES DE FLUX ---
TEMPS_ANALYSE_REQUIS = 4.0  # Latence de 4s pour être sûr
COOLDOWN_RAPPORT = 60       

# --- CHARGEMENT ---
modele_yolo = YOLO(MODELE_YOLO)
with open(FICHIER_ENCODAGES, "rb") as f:
    donnees = pickle.load(f)
encodages_connus, noms_connus = donnees["encodages"], donnees["noms"]

# --- INITIALISATION ---
video = cv2.VideoCapture(0)
compteur_frames = 0
visages_sauvegardes = []
dernier_temps_alerte = {}

verrouille = False
nom_verrouille = "ANALYSE..."
couleur_verrouille = (0, 255, 255)
debut_analyse = 0
derniere_vue_visage = 0
nb_p_precedent = 0 # Pour détecter si une nouvelle personne entre dans le champ

while True:
    succes, frame = video.read()
    if not succes: break

    compteur_frames += 1
    temps_actuel = time.time()

    if compteur_frames % ANALYSER_CHAQUE_X_FRAMES == 0:
        frame_small = cv2.resize(frame, (0, 0), fx=RESIZE_SCALE, fy=RESIZE_SCALE)
        resultats = modele_yolo(frame_small, stream=True, conf=0.5, imgsz=256, verbose=False)
        
        boxes = []
        for r in resultats:
            boxes = r.boxes
        
        nb_p_actuel = len(boxes)

        # SI ON DÉTECTE DU MONDE
        if nb_p_actuel > 0:
            derniere_vue_visage = temps_actuel
            
            # CRITIQUE : Si le nombre de personnes change, on reset pour identifier le nouveau
            if nb_p_actuel != nb_p_precedent:
                verrouille = False
                debut_analyse = temps_actuel
                nom_verrouille = "ANALYSE..."

            if not verrouille:
                if debut_analyse == 0:
                    debut_analyse = temps_actuel
                
                # Coordonnées pour l'analyse
                box = boxes[0]
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                x1, y1, x2, y2 = [int(v / RESIZE_SCALE) for v in [x1, y1, x2, y2]]

                temps_ecoule = temps_actuel - debut_analyse

                # 1. TANT QU'ON EST DANS LA LATENCE (0 à 4s)
                if temps_ecoule < TEMPS_ANALYSE_REQUIS:
                    nom_verrouille = "ANALYSE..."
                    couleur_verrouille = (0, 255, 255)
                
                # 2. LE MOMENT OÙ ON LANCE ENFIN FACE-REC (Juste après la latence)
                else:
                    visage_coupe = frame[max(0,y1):y2, max(0,x1):x2]
                    if visage_coupe.size > 0:
                        gris = cv2.cvtColor(visage_coupe, cv2.COLOR_BGR2GRAY)
                        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                        img_rgb = cv2.cvtColor(clahe.apply(gris), cv2.COLOR_GRAY2RGB)
                        
                        encodages = face_rec.face_encodings(img_rgb, known_face_locations=[(0, img_rgb.shape[1], img_rgb.shape[0], 0)])

                        if encodages:
                            dist = face_rec.face_distance(encodages_connus, encodages[0])
                            idx = np.argmin(dist)
                            
                            if dist[idx] < SEUIL_RECONNAISSANCE:
                                nom_verrouille = noms_connus[idx]
                                couleur_verrouille = (0, 255, 0)
                                autorise = True
                            else:
                                nom_verrouille = "INCONNU"
                                couleur_verrouille = (0, 0, 255)
                                autorise = False
                            
                            verrouille = True # On bloque les calculs ici
                            
                            # Alerte
                            if temps_actuel - dernier_temps_alerte.get(nom_verrouille, 0) > COOLDOWN_RAPPORT:
                                consigner_passage(nom_verrouille)
                                alerter(nom_verrouille, autorise, frame, nb_personnes=nb_p_actuel)
                                dernier_temps_alerte[nom_verrouille] = temps_actuel

            # Mise à jour des visages pour l'affichage
            visages_sauvegardes = []
            for b in boxes:
                bx1, by1, bx2, by2 = map(int, b.xyxy[0])
                bx1, by1, bx2, by2 = [int(v / RESIZE_SCALE) for v in [bx1, by1, bx2, by2]]
                visages_sauvegardes.append((bx1, by1, bx2, by2, nom_verrouille, couleur_verrouille))
            
            nb_p_precedent = nb_p_actuel

        else:
            # SI PERSONNE N'EST LÀ
            if temps_actuel - derniere_vue_visage > 2.0:
                verrouille = False
                debut_analyse = 0
                nb_p_precedent = 0
                nom_verrouille = "ANALYSE..."
                visages_sauvegardes = []

    # Affichage constant
    for (x1, y1, x2, y2, nom, couleur) in visages_sauvegardes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), couleur, 2)
        cv2.putText(frame, nom, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, couleur, 2)

    cv2.imshow("Sentinel Vision", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"): break

video.release()
cv2.destroyAllWindows()