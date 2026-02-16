import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import threading
from testing import lancer_surveillance 
from generateur_encodage import generer_base_donnees
from ajouter_personne import capture_manuelle

class SentinelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sentinel Vision v1.0")
        self.root.geometry("400x400")

        # Titre stylé
        ttk.Label(root, text="SENTINEL VISION", font=("Helvetica", 18, "bold")).pack(pady=30)

        # Style des boutons
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 11))

        # Bouton Surveillance
        self.btn_run = ttk.Button(root, text="Lancer la Surveillance", command=self.start_vision)
        self.btn_run.pack(fill='x', padx=50, pady=10)

        # Bouton Ajout
        ttk.Button(root, text="Enregistrer Nouvelle Personne", command=self.ajouter_individu).pack(fill='x', padx=50, pady=10)

        # Bouton Encodage
        ttk.Button(root, text="Mettre à jour la Base (Encodage)", command=self.refresh_db).pack(fill='x', padx=50, pady=10)

    def start_vision(self):
        # Lancement dans un thread pour ne pas bloquer l'affichage
        thread = threading.Thread(target=lancer_surveillance, daemon=True)
        thread.start()
        self.btn_run.config(state="disabled") # Sécurité : évite de lancer plusieurs caméras

    def ajouter_individu(self):
        # Boîte de dialogue pour demander le nom
        nom = simpledialog.askstring("Nouvel Utilisateur", "Entrez le nom de la personne :")
        if nom: # Si l'utilisateur n'a pas cliqué sur annuler
            messagebox.showinfo("Instructions", f"Fenêtre de capture pour : {nom}\n\n1. Regardez la caméra\n2. Appuyez sur ESPACE pour chaque photo\n3. Appuyez sur Q pour terminer")
            # On lance la capture (OpenCV ouvrira sa propre fenêtre)
            capture_manuelle(nom)

    def refresh_db(self):
        # Lance l'encodage et prévient quand c'est fini
        generer_base_donnees()
        messagebox.showinfo("Succès", "Base de données mise à jour avec succès !")

if __name__ == "__main__":
    root = tk.Tk()
    app = SentinelApp(root)
    root.mainloop()