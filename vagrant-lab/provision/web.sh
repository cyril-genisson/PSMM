#!/usr/bin/env bash

apt-get install -y nginx apache2-utils
firewall-cmd --permanent --zone=public --add-service=http
firewall-cmd --reload

for k in cyril kenny abdou
do
    echo "hello" | htpasswd -B -c /etc/nginx/.htpasswd $k
done

cat > laplateforme << WEB
server {
    listen 80;
    server_name laplateforme.lan;

    # Redirection HTTP vers HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name laplateforme.lan; # Remplacez par votre nom de domaine

    # Configuration SSL (remplacez par vos propres certificats)
    ssl_certificate /chemin/vers/votre/certificat.crt;
    ssl_certificate_key /chemin/vers/votre/cle_privee.key;

    # Autres paramètres SSL (ajustez selon vos besoins)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Authentification basique pour /laplateforme.lan/
    location /laplateforme.lan/admin/ {
        auth_basic "Zone restreinte - laplateforme.lan";
        auth_basic_user_file /etc/nginx/.htpasswd;
    }

    # Redirection vers /laplateforme.lan/ pour les requêtes sur le domaine principal
    location / {
        return 301 https://$host/laplateforme.lan/;
    }
}
WEB