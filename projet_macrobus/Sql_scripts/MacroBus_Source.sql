CREATE DATABASE MacroBus_Source;
GO
USE MacroBus_Source;

CREATE TABLE Employes (ID_Employe INT PRIMARY KEY, Nom VARCHAR(50), Prenom VARCHAR(50), Territoire VARCHAR(50), Filiale VARCHAR(50));
CREATE TABLE Produits (ID_Produit INT PRIMARY KEY, NomProduit VARCHAR(100), Categorie VARCHAR(50), PrixUnitaire DECIMAL(18,2));
CREATE TABLE Commandes (ID_Commande INT PRIMARY KEY, ID_Employe INT, DateCommande DATE, Statut VARCHAR(20));
CREATE TABLE Details_Commandes (ID_Detail INT PRIMARY KEY, ID_Commande INT, ID_Produit INT, Quantite INT, PrixVente DECIMAL(18,2));

-- Quelques données pour les tests (A partir de 2003)
INSERT INTO Employes VALUES (1, 'Durand', 'Marie', 'Europe', 'MacroBus France'), (2, 'Dubois', 'Thomas', 'Amerique', 'MacroBus Canada');
INSERT INTO Produits VALUES (10, 'Bus Ville A1', 'Urbain', 120000), (20, 'Car Tourisme Z', 'Voyage', 200000);
INSERT INTO Commandes VALUES (501, 1, '2003-05-10', 'Terminé'), (502, 2, '2003-11-15', 'Terminé');
INSERT INTO Details_Commandes VALUES (1, 501, 10, 2, 115000), (2, 502, 20, 1, 195000);