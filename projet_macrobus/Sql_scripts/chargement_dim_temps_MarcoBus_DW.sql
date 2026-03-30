USE MacroBus_DW;
GO

-- 1. On vide la table de faits (DELETE au lieu de TRUNCATE pour plus de souplesse)
DELETE FROM Fait_Ventes;

-- 2. On vide la table Dim_Temps avec DELETE
DELETE FROM Dim_Temps;

-- 3. On relance l'insertion avec le DATEPART corrigé
DECLARE @DateDebut DATE = '2003-01-01';
DECLARE @DateFin DATE = '2028-12-31';

WHILE @DateDebut <= @DateFin
BEGIN
    INSERT INTO Dim_Temps (Code_Temps, Date_Complete, Annee, Semestre, Trimestre, Mois, Nom_Mois, Jour)
    VALUES (
        YEAR(@DateDebut) * 10000 + MONTH(@DateDebut) * 100 + DAY(@DateDebut),
        @DateDebut,
        YEAR(@DateDebut),
        CASE WHEN MONTH(@DateDebut) <= 6 THEN 1 ELSE 2 END,
        DATEPART(QUARTER, @DateDebut),
        MONTH(@DateDebut),
        DATENAME(MONTH, @DateDebut),
        DATEPART(WEEKDAY, @DateDebut) -- Utilise le chiffre (1-7) pour correspondre au type INT
    );
    SET @DateDebut = DATEADD(DAY, 1, @DateDebut);
END
GO