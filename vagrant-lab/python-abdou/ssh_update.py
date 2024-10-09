import paramiko
import json
import logging
import smtplib
import requests  # Pour gérer la connexion à Alcasar via une requête HTTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import urllib3
import re

# Désactiver les avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration du système de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration de l'email
SMTP_CONFIG = {
    'sender': 'goblessmadougou@gmail.com',
    'password': 'uese axrx kwcn hjqb',
    'recipient': 'abdou.rachidou-arouna@laplateforme.io',
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}

def send_alert_email(subject, body):
    """Envoie un email d'alerte à l'administrateur système."""
    msg = MIMEMultipart()
    msg['From'] = SMTP_CONFIG['sender']
    msg['To'] = SMTP_CONFIG['recipient']
    msg['Subject'] = subject

    # Corps du mail
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_CONFIG['smtp_server'], SMTP_CONFIG['smtp_port']) as smtp:
            smtp.starttls()
            smtp.login(SMTP_CONFIG['sender'], SMTP_CONFIG['password'])
            smtp.sendmail(SMTP_CONFIG['sender'], SMTP_CONFIG['recipient'], msg.as_string())
            logging.info(f"Email envoyé à {SMTP_CONFIG['recipient']}.")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi de l'email : {e}")

def check_updates_and_reboot(server):
    """Se connecte au serveur via SSH, vérifie les mises à jour et envoie une alerte si un redémarrage est nécessaire."""
    hostname = server['hostname']
    username = server['username']
    key_file = server['key_file']
    sudo_password = server['sudo_password']

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, username=username, key_filename=key_file)
        logging.info(f"Connexion SSH réussie au serveur {hostname}.")

        # Vérifier les mises à jour (pour Debian/Ubuntu)
        stdin, stdout, stderr = client.exec_command('sudo apt update && sudo apt list --upgradable')
        stdin.write(sudo_password + '\n')  # Entrer le mot de passe sudo
        stdin.flush()

        updates = stdout.read().decode()
        if "upgradable" in updates:
            logging.info(f"Des mises à jour sont disponibles pour {hostname}. Exécution de 'sudo apt upgrade -y' ")
            # Effectuer les mises à jour
            stdin, stdout, stderr = client.exec_command(f'echo {sudo_password} | sudo -S apt upgrade -y')
            stdout.channel.recv_exit_status()  # Attendre la fin des commandes
            
            # Vérifier si un redémarrage est nécessaire
            stdin, stdout, stderr = client.exec_command('if [ -f /var/run/reboot-required ]; then echo "reboot required"; fi')
            reboot_required = stdout.read().decode().strip()
            
            if reboot_required:
                logging.info(f"Redémarrage nécessaire pour {hostname}.")
                subject = f"Alerte: Redémarrage nécessaire sur {hostname}"
                body = f"Le serveur {hostname} nécessite un redémarrage après la mise à jour."
                send_alert_email(subject, body)
            else:
                logging.info(f"Aucun redémarrage requis pour {hostname}.")
        else:
            logging.info(f"Pas de mises à jour disponibles pour {hostname}.")
        
        client.close()
        logging.info(f"Déconnexion du serveur {hostname}.")

    except Exception as e:
        logging.error(f"Erreur lors de la connexion ou de l'exécution de la commande sur {hostname} : {e}")

# Fonction pour obtenir le challenge depuis l'URL d'authentification
def get_challenge():
    url = "http://wonderfulfunsublimemorning.neverssl.com/online"  # À remplacer par l'URL correcte d'Alcasar
    
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            logging.info("Page d'authentification récupérée.")
            # Extraction du challenge à partir de l'HTML
            match = re.search(r'name="challenge" value="([^"]+)"', response.text)
            if match:
                challenge = match.group(1)
                logging.info(f"Challenge extrait : {challenge}")
                return challenge
            else:
                logging.error("Challenge non trouvé dans la page.")
                return None
        else:
            logging.error(f"Erreur lors de la récupération de la page : Statut {response.status_code}")
            return None

    except :
        logging.error(f"Erreur lors de la requête : ")
        return None

# Fonction pour se connecter à l'URL d'authentification
def login_to_authentication_site(username, password):
    challenge = get_challenge()
    if challenge is None:
        logging.error("Impossible d'obtenir le challenge.")
        return False  # Retourne False si l'authentification échoue

    login_url = "https://alcasar.laplateforme.io/intercept.php"  # Utilise l'URL Alcasar correcte ici
    
    # Données du formulaire à envoyer avec la requête POST
    data = {
        'username': username,
        'password': password,
        'challenge': challenge,
        'button': 'Authentication'  # Ce champ simule le clic sur le bouton
    }

    try:
        # Envoie de la requête POST avec les données d'authentification
        response = requests.post(login_url, data=data, verify=False, timeout=10)
        if response.status_code == 200:
            logging.info(f"Bienvenue {username} \n Authentification réussie !")
            return True  # Retourne True si l'authentification réussit
        else:
            logging.error(f"Erreur lors de la connexion: Statut {response.status_code}")
            logging.error(f"Contenu de la réponse : {response.text}")
            return False

    except :
        logging.error(f"Erreur lors de la requête de connexion : ")
        return False

def main():
    # Informations de connexion insérées directement dans le script
    username = "Entrer votre e-mail"
    password = "Votre mot de passe"  # Remplacer par le mot de passe correct

    # Connexion à Alcasar avant toute action
    if not login_to_authentication_site(username, password):
        logging.error("Impossible de se connecter à Alcasar. Abandon de la procédure.")
        return

    try:
        # Charger les informations des serveurs depuis le fichier JSON
        with open('ssh_system_mail.json', 'r') as f:
            config = json.load(f)
        
        servers = config.get('servers', [])
        if not servers:
            logging.error("Aucun serveur trouvé dans le fichier JSON.")
            return
        
        # Vérifier les mises à jour pour chaque serveur
        for server in servers:
            check_updates_and_reboot(server)

    except FileNotFoundError:
        logging.error("Le fichier JSON n'a pas été trouvé.")
    except json.JSONDecodeError:
        logging.error("Erreur lors du décodage du fichier JSON.")
    except Exception as e:
        logging.error(f"Erreur inattendue : {e}")

if __name__ == "__main__":
    main()