USE MacroBus_Source;
GO

-- 1. Nettoyage complet
TRUNCATE TABLE Details_Commandes;
DELETE FROM Produits;
DELETE FROM Employes;

-- 2. Insertion de 20 Employés avec des noms réalistes (Sénégal, France, Canada)
INSERT INTO Employes (ID_Employe, Nom, Prenom, Territoire, Filiale) VALUES 
(1, 'Ndiaye', 'Abdoulaye', 'Afrique', 'MacroBus Sénégal'),
(2, 'Leclerc', 'Jean-Pierre', 'Europe', 'MacroBus France'),
(3, 'Tremblay', 'Luc', 'Amérique', 'MacroBus Canada'),
(4, 'Sow', 'Mariama', 'Afrique', 'MacroBus Sénégal'),
(5, 'Dubois', 'Sophie', 'Europe', 'MacroBus France'),
(6, 'Gagnon', 'Marie', 'Amérique', 'MacroBus Canada'),
(7, 'Fall', 'Cheikh', 'Afrique', 'MacroBus Sénégal'),
(8, 'Moreau', 'Lucas', 'Europe', 'MacroBus France'),
(9, 'Roy', 'Sébastien', 'Amérique', 'MacroBus Canada'),
(10, 'Diop', 'Fatou', 'Afrique', 'MacroBus Sénégal'),
(11, 'Girard', 'Isabelle', 'Europe', 'MacroBus France'),
(12, 'Côté', 'Mathieu', 'Amérique', 'MacroBus Canada'),
(13, 'Gueye', 'Ibrahima', 'Afrique', 'MacroBus Sénégal'),
(14, 'Roux', 'Camille', 'Europe', 'MacroBus France'),
(15, 'Bouchard', 'Pierre', 'Amérique', 'MacroBus Canada'),
(16, 'Ba', 'Ousmane', 'Afrique', 'MacroBus Sénégal'),
(17, 'Lefebvre', 'Nicolas', 'Europe', 'MacroBus France'),
(18, 'Lavoie', 'Julie', 'Amérique', 'MacroBus Canada'),
(19, 'Kane', 'Aissatou', 'Afrique', 'MacroBus Sénégal'),
(20, 'Petit', 'Antoine', 'Europe', 'MacroBus France');

-- 3. Insertion de 10 Produits avec des noms de modèles de bus
INSERT INTO Produits (ID_Produit, NomProduit, Categorie, PrixUnitaire) VALUES 
(10, 'CityExpress A1', 'Urbain', 120000.00),
(20, 'Horizon 3000', 'Voyage', 250000.00),
(30, 'EcoShuttle V2', 'Urbain', 180000.00),
(40, 'SchoolMaster XL', 'Transport Scolaire', 85000.00),
(50, 'TurboCoach Z', 'Voyage', 320000.00),
(60, 'MiniBus Urban', 'Urbain', 75000.00),
(70, 'NightRunner 50', 'Voyage', 210000.00),
(80, 'CampusBus 20', 'Transport Scolaire', 95000.00),
(90, 'ElectroCity Evo', 'Urbain', 280000.00),
(100, 'InterState GT', 'Voyage', 350000.00);