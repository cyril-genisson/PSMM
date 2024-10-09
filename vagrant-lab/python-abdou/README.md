# Introduction du sujet 
Le but est de récupérer les logs de serveurs FTP, SQL, Web et d’archiver les tentatives d’accès avec un compte / mot de passe non valide dans des bases SQL avec envois de mail journalier à l'administrateur système. Pour cela, vous allez avoir besoin de trois serveurs : FTP, MariaDB, Web.

## Job 1: Installation des VM Debian
Nous avons trois VM serveurs sans GUI à installer (Un serveur FTP, un serveur Web et un Serveur MariaDB) 

### Configuration Hardware et Réseau du Serveur FTP 
- 1 Go Ram
- 1 Vcpu
- 8 Go HDD

### The primary network interface
allow-hotplug ens33  
iface ens33 inet static
- address 192.168.226.129
- netmask 255.255.255.0
- gatework 192.168.226.2

### Configuration Hardware et Réseau du Serveur Web (Nginx avec avec auth/basic)
Hardware :
- 1 Go Ram
- 1 Vcpu
- 8 Go HDD

### The primary network interface
allow-hotplug ens33  
iface ens33 inet static
- address 192.168.226.131
- netmask 255.255.255.0
- gatework 192.168.226.2

### Configuration Hardware et Réseau Serveur MariaDB
- 2 Go Ram
- 2 Vcpu
- 8 Go HDD

### The primary network interface
allow-hotplug ens33  
iface ens33 inet static
- address 192.168.226.133
- netmask 255.255.255.0
- gatework 192.168.226.2

### Bloquer l'accès root via ssh via une machine distant
Ajout de la ligne suivante dans le fichier sudo nano 
`"/etc/ssh/sshd_config"`
```shell
  PermitRootLogin no
```
## Job 2: Préparation de la quatrième VM(Client) ou WSL (Debian) depuis notre machine physique
Ici, nous allons utiliser WSL Debian sur notre machine

Création de notre clé ssh avec la commande `"ssh-keygen"` et la copie de la clé sur nos serveurs respectifs avec la commande `"ssh-copy-id -i "` :
```shell
  ssh-keygen -t ed25519 -C "La clé ssh pour les trois serveurs"

  ssh-copy-id -i /home/rachid/.ssh/id_ed25519.pub sql@192.168.226.133
  ssh-copy-id -i /home/rachid/.ssh/id_ed25519.pub nginx@192.168.226.131
  ssh-copy-id -i /home/rachid/.ssh/id_ed25519.pub ftpuser@192.168.226.129
```
Accéder à nos serveur depuis une machine distante :
```shell
  ssh sql@192.168.226.133
  ssh nginx@192.168.226.131
  ssh ftpuser@192.168.226.129
```

### Installation des outils nécessaires
Installer les outils et clients nécéssaires pour le test de nos serveurs
```shell
  sudo apt update
  sudo apt install mariadb-client
  sudo apt install ftp
```
Par contre en ce qui concerne les installation avec la commande `"pip"`, nous allons crée un environnement virtuel dans notre WSL pour pour installer les modules nécessaires à ce projet.

Créer un environnemt qu'on va nommer `"rachidenv"`
```shell
  sudo apt install python3.11-venv
  sudo python3 -m venv ~/rachidenv
```
Accéder à l'environnement virtuel crée :
```shell
  source ~/rachidenv/bin/activate
```
Installer les packages nécessaires :
```shell
  pip install yagmail requests
```
Créer un répertoire pour y mettre nos scripts
```shell
  mkdir pycripts
```

## Job 3: Script `"ssh_login.py" / "connexion.json"`
Nous devons faire un script “ssh_login.py”, qui depuis la VM , va se connecter
sur un des serveurs et lancer une commande shell (par exemple «df» ou «ls»
ou autre).

## Job 4: script + fichier .json `"ssh_login_sudo.py" / "connexion.json`
Nous allons utiliser le script précédent pour faire un script
“ssh_login_sudo.py”, qui depuis la VM, va se connecter sur un des serveurs
et lancer une commande shell, cette fois en mode «sudo».

## Job 5: script + fichier .json `"ssh_mysql.py" / "connexion_mysql.json"`
Maintenant que nous pouvons lancer des commandes shell en «sudo» , nous allons nous
connecter sur le serveur MariaDB/MySQL.
Nous allons faire un script `ssh_mysql.py`, pour vérifier que nous avons bien
accès au serveur MariaDB/MySQL.

## Job 6:
### Plan général :
- Créer la base de données et les tables nécessaires.
- Configurer MariaDB/MySQL pour enregistrer les tentatives d'accès échouées dans les logs.
- Écrire le script ssh_mysql_error.py pour lire les logs, extraire les informations pertinentes, et les stocker dans la base de données.
- Tester le système en faisant des tentatives de connexion avec des identifiants incorrects.

### Création de la base de données et des tables
Connexion à la base de donnée
```shell
  mariadb -u sql -p
```
Crée une base de données pour stocker les logs des accès échoués :
```sql
CREATE DATABASE ssh_access_logs;
```
Sélectionner la base de données :
```sql
USE ssh_access_logs;
```

Crée une table pour stocker les informations sur les tentatives d'accès échouées. Cette table va contenir le nom d'utilisateur utilisé, l'IP de l'utilisateur ayant tenté de se connecter, et la date/heure de la tentative :

```sql
CREATE TABLE failed_logins_mariadb(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    ip_address VARCHAR(45),
    attempt_time TIMESTAMP
);
```
Cette table contient trois colonnes :
- username : le nom d'utilisateur ayant échoué à se connecter.
- ip_address : l'adresse IP de la machine ayant tenté la connexion.
- attempt_time : la date et l'heure de la tentative d'accès.

### Configuration des logs de MariaDB
Pour enregistrer les erreurs de connexion dans les logs, il faut s'assurer que la journalisation des erreurs (error logs) est activée dans la configuration de MySQL/MariaDB.

```shell
  sudo nano /etc/mysql/my.cnf
```
Ajouter les paramètres suivantes :
```shell
  [mysqld]
log_error = /var/log/mysql/error.log
log_warnings = 2
```
- log_error : Définit l'emplacement où les logs d'erreur seront enregistrés.
- log_warnings : Enregistre les avertissements et les tentatives d'accès échouées.

Redémarre MariaDB pour appliquer les changements :
```shell
  sudo systemctl restart mysql
  sudo systemctl restart mariadb
```
Génère des erreurs d'accès en essayant de se connecter avec des mauvais identifiants :
```shell
  mariadb -u test -test
```
Cette commande va enregistrer des tentatives échouées dans le fichier de log sous la forme suivante quand nous faisons un "cat" de `/var/log/mysql/error.log` :
```shell
  cat /var/log/mysql/error.log
```
La sortie de la commande affichera quelque chose comme ça
`2024-09-21 14:04:15 31 [Warning] Access denied for user 'test'@'localhost' (using password: NO)`

Le script `ssh_mysql_error.py` (Voir le script )

### Permettre à mon utilisateur `sql` pour se connecter ma db et lui donner les privilèges  nécéssaires :
```sql
CREATE USER 'sql'@'192.168.226.1' IDENTIFIED BY 'sql';
```
On remarque qu'on a spécifié une adresse IP `192.168.226.1` et non `localhost` parce qu'on veut que l'utilisateur puisse se connecter depuis une addresse IP spécifique qui est le `192.168.226.133` (adresse IP du serveur sql). 
Par conséquent on a mis le `192.168.226.1` pour l'utilisateur `sql` par ce que quand on essaye de se connecter à MariaDB depuis le WSL l'adresse IP `192.168.226.1` est perçu comme la passerelle du WSL vers le Serveur MariaDB.

### Changer le localhost en spécifiant une addresse IP spécifique
Ouvrir le fichier `/etc/mysql/mariadb.conf.d/50-server.cnf` et modifier la ligne :
`bind-address            = 192.168.226.133`

### Décommenter les lignes suivantes pour la gestion des logs :
```shell
  general_log_file       = /var/log/mysql/mysql.log
  general_log            = 1
```

```shell
  log_error = /var/log/mysql/error.log
```
### Vérifier si le serveur MariaDB écoute sur le port `3306` et l'adresse qu'on a spécifié 
```shell
  sudo ss -tuln | grep 3306
```
Résultat : 
`tcp   LISTEN 0      80     192.168.226.133:3306      0.0.0.0:*`
On peut constater que toutes les configuration sont prises en comptes :

### Maintenant, on peut se connecter depuis notre WSL avec la commande :
```shell
  mysql -u sql -p -h 192.168.226.133
```
### Ou encore choisir directement une base de données :
```shell
  mysql -u sql -p -h 192.168.226.133 ssh_access_logs
```
### En ce qui concerne le script pour récupérer les mauvais tentatives d'accès au serveur MariaDB dans le fichier des logs et les insérer dans la base de données > voir le script `ssh_mysql_error.py` et le fichier .json `ssh_mysql_error.json`

## Job 7 :
On va désormais s’attaquer au serveur FTP, sur votre poste installer FileZilla et
accéder au serveur FTP, et depuis la VM depuis un client FTP en CLI
Faites plusieurs accès avec des utilisateurs/MdP qui ne sont pas bons (pour
que le serveur FTP génère des logs avec des erreurs d’accès).

Écrire le script `ssh_ftp_error.py`, pour qu’il récupère les logs d’erreur et les
écrire dans votre base de données.

### En ce qui concerne le script pour récupérer les mauvais tentatives d'accès au serveur MariaDB dans le fichier des logs et les insérer dans la base de données > voir le script `ssh_ftp_error.py` et le fichier .json `ssh_ftp_error.json`

Crée une table pour stocker les informations sur les tentatives d'accès échouées. Cette table va contenir le nom d'utilisateur utilisé, l'IP de l'utilisateur ayant tenté de se connecter, et la date/heure de la tentative :

```sql
CREATE TABLE failed_logins_ftp(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    ip_address VARCHAR(45),
    attempt_time TIMESTAMP
);
```
Cette table contient trois colonnes :
- username : le nom d'utilisateur ayant échoué à se connecter.
- ip_address : l'adresse IP de la machine ayant tenté la connexion.
- attempt_time : la date et l'heure de la tentative d'accès.

## Job 8 :
On va maintenant s’attaquer au serveur Web. Le serveur Web est protégé par
un compte utilisateur et mot de passe.
Faites plusieurs accès avec des utilisateurs / MdP qui ne sont pas bons (pour
que le serveur Web génère des logs avec des erreurs d’accès).
Écrire le script `ssh_web_error.py`, pour récupérer les logs d’erreurs et les
écrire dans votre base de données.

Crée une table pour stocker les informations sur les tentatives d'accès échouées. Cette table va contenir le nom d'utilisateur utilisé, l'IP de l'utilisateur ayant tenté de se connecter, et la date/heure de la tentative :

```sql
CREATE TABLE failed_logins_web(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255),
    ip_address VARCHAR(45),
    attempt_time TIMESTAMP
);
```

Cette table contient trois colonnes :
- username : le nom d'utilisateur ayant échoué à se connecter.
- ip_address : l'adresse IP de la machine ayant tenté la connexion.
- attempt_time : la date et l'heure de la tentative d'accès.

## Job 9 :
Maintenant que l’on a créé nos bases SQL avec les erreurs d’accès, il va falloir
avertir l’administrateur. Il faut écrire un script “ssh_serveur_mail.py”, qui va
envoyer un mail à l'administrateur avec les historiques des tentatives de
connexion de la veille.

### Étapes à suivre :
- Connexion à la base de données pour récupérer les tentatives de connexion échouées de la veille.
- Extraction des données sous un format lisible.
- Envoi d’un email à l’administrateur avec les logs de ces tentatives.

### Structure générale du script ssh_serveur_mail.py :
- Importer les modules nécessaires pour la gestion de la base de données et l'envoi de mails.
- Se connecter à la base de données.
- Récupérer les logs de la veille.
- Construire un rapport avec les logs.
- Configurer l'envoi d'email et envoyer le rapport.


### SSH Serveur Mail
Ce script Python `ssh_serveur_mail.py` récupère les tentatives de connexion SSH échouées depuis une base de données MySQL et envoie un rapport par e-mail. Il supporte deux méthodes d'envoi d'e-mails : SendGrid et SMTP Gmail.

#### Prérequis
- Python 3.x
- MySQL
- Bibliothèques Python :
  - mysql-connector-python
  - smtplib (intégré)
  - sendgrid (si vous utilisez SendGrid)
  - Installez les bibliothèques nécessaires avec la commande :
```shell
  pip install mysql-connector-python sendgrid
```
#### Configuration
Créez un fichier `ssh_serveur_mail.json` avec les informations de configuration de la base de données et de (l'e-mail. Voir le fichier `ssh_serveur_mail.json` contenant la configuration avec sendGrid utilisant une clé API)
Fichier ssh_serveur_mail.json (SendGrid) :
```json
{
    "db_config": {
        "user": "nom d'utlisateur",
        "password": "passwd utilisateur",
        "host": "IP du serveur",
        "database": "nom de la base de données"
    },
    "email_config": {
        "sender": "your_verified_email@domain.com",
        "recipient": "recipient_email@domain.com",
        "clé": "clé api"
    }
}
;
```

##### Méthode 1 : Envoi d'e-mails avec SendGrid
- Ajoutez votre clé API SendGrid dans le fichier ssh_serveur_mail.json.
- Utilisez une adresse e-mail vérifiée par SendGrid comme expéditeur.

 Fichier ssh_serveur_mail.json (SMTP Gmail) :
 ```json
{
    "db_config": {
        "user": "sql",
        "password": "sql",
        "host": "192.168.226.133",
        "database": "ssh_access_logs"
    },
    "email_config": {
        "sender": "your_email@gmail.com",
        "password": "your_gmail_app_password",
        "recipient": "recipient_email@gmail.com",
        "smtp_server": "smtp.gmail.com",
        "smtp_port": 587
    }
}
```
##### Méthode 2 : Envoi d'e-mails avec SMTP Gmail
- Activez la validation en deux étapes sur votre compte Google.
- Générez un mot de passe d'application dans les paramètres de sécurité de Google.
- Utilisez le mot de passe dans la configuration email_config.