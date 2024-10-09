#!/usr/bin/env bash

apt-get install -y vsftpd apache2-utils
firewall-cmd --permanent --zone=public --add-service=ftp
firewall-cmd --reload

cat > vsftpd.conf << FTP
# Fichier: /etc/vsftpd.conf

# Paramètres généraux
listen=YES
listen_ipv6=NO 
anonymous_enable=NO # Désactiver les connexions anonymes
local_enable=YES   # Autoriser les connexions locales (utilisateurs du système)
write_enable=YES   # Autoriser l'écriture (upload) de fichiers

# Utilisateurs virtuels
guest_enable=YES
guest_username=ftpuser # Nom d'utilisateur unique pour tous les utilisateurs virtuels
virtual_use_local_privs=YES # Donner les mêmes droits qu'un utilisateur local

# Authentification par mot de passe
pam_service_name=vsftpd 
userlist_enable=YES
userlist_file=/etc/vsftpd.userlist
userlist_deny=NO # Autoriser les utilisateurs de la liste

# Sécurité
chroot_local_user=YES # Confiner les utilisateurs dans leur répertoire personnel
allow_writeable_chroot=YES # Nécessaire pour écrire dans un répertoire chrooté
hide_ids=YES # Masquer les IDs des utilisateurs dans les messages du serveur
secure_chroot_dir=/var/run/vsftpd/empty # Répertoire chrooté sécurisé
chmod_enable=YES # Autoriser vsftpd à changer les permissions des fichiers uploadés
local_umask=022 # Masque de création de fichiers pour les utilisateurs locaux

# Performances
pasv_enable=YES
pasv_min_port=40000
pasv_max_port=50000
max_clients=10
max_per_ip=3

# Configuration SSL/TLS pour FTPS
ssl_enable=YES
rsa_cert_file=/chemin/vers/votre/certificat.crt
rsa_private_key_file=/chemin/vers/votre/cle_privee.key

# Forcer l'utilisation de SSL/TLS pour les connexions de contrôle et de données
force_local_data_ssl=YES
force_local_logins_ssl=YES

# Autoriser uniquement les connexions TLS sécurisées (désactiver SSLv2 et SSLv3)
ssl_tlsv1_3=YES
ssl_tlsv1_2=YES
ssl_tlsv1_1=NO
ssl_tlsv1=NO
ssl_sslv2=NO
ssl_sslv3=NO
FTP

#cat vsftpd.conf > /etc/vsftpd.conf

echo "hello" | htpasswd -i -c /etc/vsftpd.userlist cyril
echo "hello" | htpasswd -i /etc/vsftpd.userlist abdou
echo "hello" | htpasswd -i /etc/vsftpd.userlist kenny

mkdir -p /home/vsftpd/{cyril,adbou,kenny}
chown root:root /home/vsftpd
chmod 755 /home/vsftpd
chown ftp:ftp /home/vsftpd/*
chmod 700 /home/vsftpd/*

#systemctl restart vsftpd
