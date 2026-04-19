CREATE DATABASE IF NOT EXISTS educollect_v2
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE educollect_v2;


CREATE TABLE IF NOT EXISTS reponses (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  matricule       VARCHAR(30)  NOT NULL UNIQUE,   -- 1 réponse par matricule
  niveau          ENUM('L1','L2','L3','Master 1','Master 2') NOT NULL,
  filiere         VARCHAR(80)  NOT NULL,
  soumis_le       DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS matieres_difficiles (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  reponse_id  INT NOT NULL,
  matiere     VARCHAR(120) NOT NULL,
  FOREIGN KEY (reponse_id) REFERENCES reponses(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS matieres_pratique (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  reponse_id  INT NOT NULL,
  matiere     VARCHAR(120) NOT NULL,
  FOREIGN KEY (reponse_id) REFERENCES reponses(id) ON DELETE CASCADE
);
