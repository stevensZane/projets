import cv2
import os
import numpy as np

def capture_manuelle(nom_personne):
    """
    Ouvre la caméra et capture une photo à chaque appui sur ESPACE.
    Appuyez sur 'q' pour quitter une fois terminé.
    """
    # 1. Préparation du dossier
    dossier_cible = os.path.join("personnes", nom_personne.upper())
    if not os.path.exists(dossier_cible):
        os.makedirs(dossier_cible)
    
    video = cv2.VideoCapture(0)
    compteur = 0

    print(f"--- MODE ENREGISTREMENT : {nom_personne.upper()} ---")
    print("Instructions :")
    print("- [ESPACE] : Prendre une photo")
    print("- [Q] : Terminer et fermer")

    while True:
        succes, frame = video.read()
        if not succes:
            break

        # On affiche les instructions en temps réel sur l'image
        affichage = frame.copy()
        cv2.putText(affichage, f"Photos prises : {compteur}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(affichage, "ESPACE pour capturer | Q pour quitter", (10, frame.shape[0] - 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow("Capture Manuelle - Sentinel Vision", affichage)
        
        touche = cv2.waitKey(1) & 0xFF
        
        # Appui sur ESPACE (code ASCII 32)
        if touche == ord(' '):
            compteur += 1
            nom_fichier = os.path.join(dossier_cible, f"{nom_personne}_{compteur}.jpg")
            cv2.imwrite(nom_fichier, frame)
            print(f"[OK] Photo {compteur} enregistrée dans {dossier_cible}")
            
            # Petit flash visuel pour confirmer la capture
            cv2.imshow("Capture Manuelle - Sentinel Vision", 255 * np.ones(frame.shape, dtype=np.uint8))
            cv2.waitKey(50)

        # Appui sur Q pour quitter
        elif touche == ord('q'):
            break

    video.release()
    cv2.destroyAllWindows()
    print(f"Terminé. {compteur} photos ajoutées pour {nom_personne}.")
