StreamData est une application web interactive permettant aux utilisateurs de scraper, visualiser et analyser des données facilement. Grâce à une interface intuitive, les utilisateurs peuvent uploader des fichiers, explorer des données et générer des graphiques.

**Structure du projet**
``` bash
📦 StreamData
├── 📁 images               # le logo de l'appli y est contenu
├── 📁 upload_files         # repertoire contenant tous les fichiers
│   ├── main.py              # Fichier principal Streamlit, toutes les pages y sont contenues
│   ├── utils.py             # Fonctions utilitaires   
│   ├── requirements.txt     # Dépendances du projet
│   └── README.md            # Ce fichier 📌
```

**Fonctionnalités**
- Télécharger des fichiers (CSV, EXCEL)
- Visualisation des données avec des graphes
- Explorer les colonnes selon leurs types de données
- Formulaire d'évaluation

**Installation & Exécution**
Préréquis
`pip install streamlit pandas matplotlib seaborn`

**Lancer l'application**
`streamlit run main.py`


Les pages
- Acceuil -- La page de présentation
- Scraper  -- Scraper selon la categorie du site coinafrique
- Upload -- Charger des fichiers (csv ou xlsx) depuis votre ordinateur
- Visualisation -- Avoir des informations descriptives d'un fichier sauvegardé dans Bibliothèque
- Bibliothèque -- Tous les fichiers y sont stockés. A la fin du scraping le fichier est automatiquement sauvegarder dans Bibliothèque, mais aussi tous les chargés à partir de votre appareil seront automatquement sauvegardés
- Feedback -- Cette page permet aux utilisateurs de faire des retours par rapport à leur experience sur l'appli


Cette application est en cours de développement. Toute suggestion d'amélioration est la bienvenue !
Si vous avez des questions ou des suggestions, n'hésitez pas à me contacter à lasiebazoungoula@gmail.com