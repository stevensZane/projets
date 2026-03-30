USE MacroBus_Source;
GO

-- 1. Nettoyage des anciennes commandes uniquement
TRUNCATE TABLE Details_Commandes;
DELETE FROM Commandes;

-- 2. Variables pour la génération
DECLARE @i INT = 1;
DECLARE @TotalCommandes INT = 10000;
DECLARE @StartDate DATETIME = '2003-01-10'; -- Ta date de départ
DECLARE @CurrentDate DATETIME;
DECLARE @RandomEmp INT;
DECLARE @RandomProd INT;
DECLARE @RandomQty INT;
DECLARE @BasePrix DECIMAL(18,2);

-- Désactiver les contraintes de log pour accélérer l'insertion si nécessaire
SET NOCOUNT ON;

WHILE @i <= @TotalCommandes
BEGIN
    -- Distribution des dates : On ajoute environ 1 à 2 heures entre chaque commande 
    -- pour étaler les 10 000 commandes sur 2003-2004-2005 de manière réaliste.
    SET @CurrentDate = DATEADD(MINUTE, (@i * 120) + ABS(CHECKSUM(NEWID()) % 60), @StartDate);

    -- Sélection aléatoire basée sur tes scripts fournis
    SET @RandomEmp = (ABS(CHECKSUM(NEWID()) % 20) + 1); -- IDs 1 à 20
    SET @RandomProd = ((ABS(CHECKSUM(NEWID()) % 10) + 1) * 10); -- IDs 10, 20... 100
    SET @RandomQty = (ABS(CHECKSUM(NEWID()) % 5) + 1); -- Quantité 1 à 5

    -- Récupération du prix unitaire du produit pour le détail
    SELECT @BasePrix = PrixUnitaire FROM Produits WHERE ID_Produit = @RandomProd;

    -- Insertion de l'entête de commande
    INSERT INTO Commandes (ID_Commande, ID_Employe, DateCommande, Statut)
    VALUES (@i, @RandomEmp, @CurrentDate, 'Terminé');

    -- Insertion du détail (avec une variation de prix de -5% à +5% pour le réalisme)
    INSERT INTO Details_Commandes (ID_Detail, ID_Commande, ID_Produit, Quantite, PrixVente)
    VALUES (@i, @i, @RandomProd, @RandomQty, @BasePrix * (0.95 + (RAND() * 0.1)));

    SET @i = @i + 1;
END