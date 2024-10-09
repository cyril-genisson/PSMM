#!/usr/bin/env bash

if [ ! -f /etc/apt/sources.list.d/mariadb.list ]
then
    curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash
    apt update 2&>1 /dev/null
    apt-get install -y mariadb-server
fi

cat > create_base_logs.sql << SQL
-- Fichier : creation_base_logs.sql

-- Création de la base de données si elle n'existe pas déjà
CREATE DATABASE IF NOT EXISTS logs;

-- Utilisation de la base de données
USE logs;

-- Création de la table 'web' pour logguer les erreurs de connexions
CREATE TABLE IF NOT EXISTS web (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    username VARCHAR(50) NOT NULL,
    ip VARCHAR(15),
    log_info TEXT
);

-- Création de la table 'db' pour logguer les erreurs de connexions
CREATE TABLE IF NOT EXISTS db (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    username VARCHAR(50) NOT NULL,
    ip VARCHAR(15),
    log_info TEXT
);

-- Création de la table 'ftp' pour logguer les erreurs de connexions
CREATE TABLE IF NOT EXISTS ftp (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    username VARCHAR(50) NOT NULL,
    ip VARCHAR(15),
    log_info TEXT
);

-- Création de la table 'system' pour logguer les ressources systèmes
CREATE TABLE IF NOT EXISTS system (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date TIMESTAMP NOT NULL,
    host VARCHAR(20) NOT NULL,
    ram VARCHAR(5) NOT NULL,
    disk VARCHAR(5) NOT NULL,
);


CREATE USER IF NOT EXISTS 'monitor'@'localhost' IDENTIFIED BY 'monitor';
GRANT ALL PRIVILEGES ON logs.* TO 'monitor'@'localhost';

-- Rechargement des privilèges pour que les changements prennent effet
FLUSH PRIVILEGES;
SQL

mariadb -u root < create_base_logs.sql
