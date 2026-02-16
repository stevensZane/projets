import cv2
import face_recognition as face_rec
import os
import pickle
import numpy as np


def appliquer_filtres(image):
    """
    Génère des versions traitées pour enrichir la base d'encodage.
    Multiplier les prétraitements permet de rendre la reconnaissance 
    robuste aux variations d'éclairage et de bruit.
    """
    augmentations = []
    gris = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 1. Gris Standard
    augmentations.append(cv2.cvtColor(gris, cv2.COLOR_GRAY2BGR))

    # 2. CLAHE (Contrast Limited Adaptive Histogram Equalization) - LE PLUS PRÉCIS
    #Améliore le contraste local sans saturer l'image
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gris_clahe = clahe.apply(gris)
    augmentations.append(cv2.cvtColor(gris_clahe, cv2.COLOR_GRAY2BGR))

    # 3. Égalisation d'Histogramme Globale
    gris_egalise = cv2.equalizeHist(gris)
    augmentations.append(cv2.cvtColor(gris_egalise, cv2.COLOR_GRAY2BGR))

    # 4. Filtre Gaussien (Réduction du bruit capteur)
    augmentations.append(cv2.GaussianBlur(image, (5, 5), 0))

    # 5. Convolution : Netteté (Rehaussement des traits du visage)
    noyau = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    augmentations.append(cv2.filter2D(image, -1, noyau))

    # 6. Luminosité augmentée (+30%)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.3, 0, 255)
    augmentations.append(cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR))

    return augmentations


def generer_base_donnees(dossier_racine='personnes'):
    encodages_connus = []
    noms_connus = []

    if not os.path.exists(dossier_racine):
        print(f"Erreur : Le dossier {dossier_racine} n'existe pas.")
        return

    for nom_personne in os.listdir(dossier_racine):
        chemin_dossier = os.path.join(dossier_racine, nom_personne)
        
        if os.path.isdir(chemin_dossier):
            print(f"Traitement de : {nom_personne}...")
            
            for fichier in os.listdir(chemin_dossier):
                # IMPORTANT : On ignore les images déjà augmentées pour éviter les boucles
                if fichier.startswith("aug_"): 
                    continue
                
                chemin_img = os.path.join(chemin_dossier, fichier)
                img = cv2.imread(chemin_img)
                if img is None: continue
                
                noms_filtres = ["ORIGINAL", "GRIS", "CLAHE", "EGALISE", "FLOU", "NETTETE", "LUMIERE"]

               # On prépare toutes les versions (Originale + les 6 filtres)
                images_a_traiter = [img] + appliquer_filtres(img)

                for i, image_variante in enumerate(images_a_traiter):
                    
                    # Pipeline : Conversion RGB obligatoire pour face_recognition
                    img_rgb = cv2.cvtColor(image_variante, cv2.COLOR_BGR2RGB)
                    encodages = face_rec.face_encodings(img_rgb)
                    
                    if len(encodages) > 0:
                        encodages_connus.append(encodages[0])
                        noms_connus.append(nom_personne.upper())
                        
                        # Sauvegarde uniquement des augmentations (i > 0)
                        # On ne sauve pas l'index 0 car l'originale est déjà dans le dossier.
                        if i > 0:
                            suffixe = noms_filtres[i]
                            nom_fichier_aug = f"aug_{suffixe}_{fichier}"
                            cv2.imwrite(os.path.join(chemin_dossier, nom_fichier_aug), image_variante)

    # Sauvegarde finale avec la clé "noms"
    with open('encodages.pickle', 'wb') as f:
        pickle.dump({"encodages": encodages_connus, "noms": noms_connus}, f)
    
    print(f"Terminé ! {len(encodages_connus)} visages encodés dans encodages.pickle")

if __name__ == "__main__":
    generer_base_donnees()