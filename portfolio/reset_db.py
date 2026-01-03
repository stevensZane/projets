# Créez un fichier reset_db.py à la racine
import os
import subprocess
import sys

def reset_database():
    """Réinitialise complètement la base de données"""
    print("🔧 Réinitialisation de la base de données...")
    
    # Supprime la base de données existante
    if os.path.exists('db.sqlite3'):
        os.remove('db.sqlite3')
        print("🗑️  db.sqlite3 supprimé")
    
    # Supprime les anciennes migrations
    migrations_dir = 'main/migrations'
    if os.path.exists(migrations_dir):
        for file in os.listdir(migrations_dir):
            if file.endswith('.py') and file != '__init__.py':
                os.remove(os.path.join(migrations_dir, file))
                print(f"🗑️  {file} supprimé")
    
    # Crée les migrations
    print("📦 Création des migrations...")
    subprocess.run([sys.executable, 'manage.py', 'makemigrations', 'main'])
    
    # Applique les migrations
    print("🚀 Application des migrations...")
    subprocess.run([sys.executable, 'manage.py', 'migrate'])
    
    # Crée un superutilisateur
    print("👑 Création d'un superutilisateur...")
    subprocess.run([sys.executable, 'manage.py', 'createsuperuser'])
    
    print("✅ Base de données réinitialisée avec succès!")
    print("👉 Lancez le serveur : python manage.py runserver")

if __name__ == '__main__':
    reset_database()