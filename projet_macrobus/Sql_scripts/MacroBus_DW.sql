IF DB_ID('MacroBus_DW') IS NOT NULL
BEGIN
    ALTER DATABASE MacroBus_DW SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE MacroBus_DW;
END
GO

CREATE DATABASE MacroBus_DW;
GO
USE MacroBus_DW;

CREATE TABLE Dim_Temps (
    Code_Temps INT PRIMARY KEY, -- Format AAAAMMJJ
    Date_Complete DATE,
    Annee INT,
    Semestre INT,
    Trimestre INT,
    Mois INT,
    Nom_Mois VARCHAR(20),
    Jour INT
);

CREATE TABLE Dim_Commercial (
    Cle_Commercial INT PRIMARY KEY IDENTITY(1,1),
    ID_Source_Employe INT,
    Nom_Complet NVARCHAR(100),
    Territoire VARCHAR(50),
    Filiale VARCHAR(50)
);

CREATE TABLE Dim_Produit (
    Cle_Produit INT PRIMARY KEY IDENTITY(1,1),
    ID_Source_Produit INT,
    Nom_Produit VARCHAR(100),
    Categorie_Produit VARCHAR(50)
);

CREATE TABLE Fait_Ventes (
    ID_Fait INT PRIMARY KEY IDENTITY(1,1),
    Code_Temps INT,
    Cle_Commercial INT,
    Cle_Produit INT,
    Quantite INT,
    Montant_Total DECIMAL(18,2),
    FOREIGN KEY (Code_Temps) REFERENCES Dim_Temps(Code_Temps),
    FOREIGN KEY (Cle_Commercial) REFERENCES Dim_Commercial(Cle_Commercial),
    FOREIGN KEY (Cle_Produit) REFERENCES Dim_Produit(Cle_Produit)
);