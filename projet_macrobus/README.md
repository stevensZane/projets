🚍 Projet ETL MacroBus - Data Warehouse

Ce projet implémente un flux ETL (Extract, Transform, Load) complet pour l'entreprise MacroBus. L'objectif est de migrer des données d'une base transactionnelle (Source) vers un entrepôt de données (DW) structuré en schéma en étoile.
📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé les outils suivants :

    Docker Desktop (pour l'instance SQL Server)

    SQL Server Management Studio (SSMS)

    Visual Studio avec l'extension SSIS (SQL Server Integration Services)

    Power BI Desktop

🚀 Guide de déploiement (Étape par étape)
1. Lancement de l'infrastructure

Démarrez le conteneur SQL Server à l'aide de Docker Compose :
Bash

docker-compose up -d

    Note : Assurez-vous que le port 1433 est libre sur votre machine hôte.

2. Préparation des Bases de Données

Ouvrez SSMS et exécutez les scripts SQL dans cet ordre précis pour initialiser l'environnement :

    MacroBus_Source.sql : Création des tables transactionnelles.

    MacroBus_DW.sql : Création du schéma de l'entrepôt (Dimensions et Faits).

    Alimentation_employéXproduits.sql : Alimenter la bdd avec des employés et les produits 

    Alimentation_Source_1000.sql : Génération de 100 lignes de ventes pour les tests.

    Chargement_Dim_Temps.sql : Remplissage du calendrier (période 2003-2028).
3. Exécution du flux ETL (SSIS)

Ouvrez la solution SSIS dans Visual Studio :

    Ouvrez le projet dans Visual Studio. J'ai configuré un Control Flow qui ordonnance les tâches automatiquement :

     Premier lancement de Visual Studio
        1. Ouverture du projet

            Ne double-clique pas sur le fichier .dtsx directement.

            Ouvre le fichier de solution ETL_Macrobus.slnx (ou .sln) que tu vois dans le dossier.

            Cela permet à Visual Studio de charger tout le contexte, y compris les gestionnaires de connexion.

        2. Configuration des connexions (Obligatoire)

        Dès que le projet est ouvert, tu verras probablement des petites croix rouges. C'est normal, VS essaie de se connecter à mon SQL Server. Tu dois le pointer vers le tien (Docker) :

            Regarde en bas de l'écran dans la fenêtre "Gestionnaires de connexion" ou "Connexion Managers".

            Tu verras deux connexions (ex: LocalHost.MacroBus_Source et LocalHost.MacroBus_DW).

            Fais un clic droit sur l'une d'elles > Modifier.

            Dans la fenêtre qui s'ouvre :

                Nom du serveur : Tape localhost,1433.

                Authentification : Sélectionne "Authentification SQL Server".

                Nom d'utilisateur / Mot de passe : Entre tes identifiants Docker (ceux du docker-compose.yml).

                Sélectionner une base de données : Choisis la base correspondante (MacroBus_Source ou MacroBus_DW).

            Clique sur Tester la connexion. Répète l'opération pour la deuxième connexion.

        3. Exécution "One-Click"

        Une fois les connexions vertes :

            Assure-toi d'être sur l'onglet Control Flow (Flux de contrôle).

            Tu verras les boîtes reliées par des flèches : les dimensions se chargent en premier, puis la table de fait.

            Appuie sur le bouton Démarrer (flèche verte en haut) ou sur F5.

            Validation : Quand tout devient vert, les 100 lignes sont officiellement dans ton entrepôt !


4. Analyse dans Power BI

Connectez Power BI Desktop à votre base de données MacroBus_DW :

    Importation : Chargez les tables Fait_Ventes, Dim_Commercial, Dim_Produit et Dim_Temps.

    Modélisation : Vérifiez que les relations sont basées sur les Clés Techniques (Cle_Commercial, Cle_Produit, Code_Temps) et non sur les IDs sources.
