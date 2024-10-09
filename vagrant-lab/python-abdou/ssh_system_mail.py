import paramiko
import json
import mysql.connector
import logging
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

# Configuration du système de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Seuils d'alerte
CPU_THRESHOLD = 5  # Pourcentage d'utilisation du CPU
RAM_THRESHOLD = 10   # Pourcentage d'utilisation de la RAM
DISK_THRESHOLD = 8  # Pourcentage d'utilisation du disque

# Configuration email incluse dans le code
SMTP_CONFIG = {
    'sender': 'goblessmadougou@gmail.com',
    'password': 'uese axrx kwcn hjqb',
    'recipient': 'abdou.rachidou-arouna@laplateforme.io',
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587
}

def send_alert_email(smtp_config, server, cpu, ram, disk):
    """Envoie un email d'alerte à l'administrateur."""
    subject = f"Alerte de système sur {server}"

    # Corps de l'e-mail avec HTML
    body = f"""
    <html>
    <head>
        <style>
            table {{
                width: 50%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 1em;
                font-family: sans-serif;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            }}
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #dddddd;
            }}
            tr:nth-child(even) {{
                background-color: #f2f2f2;
            }}
            tr:hover {{
                background-color: #f1f1f1;
            }}
            th {{
                background-color: #4CAF50;
                color: white;
            }}
        </style>
    </head>
    <body>
        <h2>Alerte de système pour le serveur {server}</h2>
        <table>
            <tr>
                <th>Ressource</th>
                <th>Utilisation</th>
            </tr>
            <tr>
                <td>Utilisation CPU</td>
                <td>{cpu}</td>
            </tr>
            <tr>
                <td>Utilisation RAM</td>
                <td>{ram}</td>
            </tr>
            <tr>
                <td>Utilisation Disque</td>
                <td>{disk}</td>
            </tr>
        </table>
    </body>
    </html>
    """

    msg = MIMEText(body, 'html')  # Indiquer que le corps est du HTML
    msg['Subject'] = subject
    msg['From'] = smtp_config['sender']
    msg['To'] = smtp_config['recipient']

    try:
        with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port']) as smtp_server:
            smtp_server.starttls()
            smtp_server.login(smtp_config['sender'], smtp_config['password'])
            smtp_server.send_message(msg)
            logging.info(f"Email d'alerte envoyé à {smtp_config['recipient']}.")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi de l'email : {e}")


class SystemStatus:
    def __init__(self, db_config):
        self.db_config = db_config

    def connect_db(self):
        """Connexion à la base de données."""
        try:
            self.conn = mysql.connector.connect(**self.db_config)
            self.cursor = self.conn.cursor()
            logging.info("Connexion à la base de données réussie.")
        except mysql.connector.Error as err:
            logging.error(f"Erreur de connexion à la base de données : {err}")

    def close_db(self):
        """Ferme la connexion à la base de données."""
        if self.conn:
            self.cursor.close()
            self.conn.close()
            logging.info("Connexion à la base de données fermée.")

    def store_status(self, server, cpu, ram, disk):
        """Stocke les informations d'état dans la base de données."""
        try:
            query = "INSERT INTO system_status (server, cpu, ram, disk, timestamp) VALUES (%s, %s, %s, %s, %s)"
            timestamp = datetime.now()
            self.cursor.execute(query, (server, cpu, ram, disk, timestamp))
            self.conn.commit()
            logging.info(f"Données stockées pour le serveur {server}.")
        except mysql.connector.Error as err:
            logging.error(f"Erreur lors de l'insertion dans la base de données : {err}")

    def cleanup_old_entries(self):
        """Supprime les entrées de plus de 24 heures."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            query = "DELETE FROM system_status WHERE timestamp < %s"
            self.cursor.execute(query, (cutoff_time,))
            self.conn.commit()
            logging.info("Anciennes entrées supprimées.")
        except mysql.connector.Error as err:
            logging.error(f"Erreur lors de la suppression des anciennes entrées : {err}")

    def get_system_status(self, hostname, username, key_file):
        """Récupère l'état du système via SSH."""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname, username=username, key_filename=key_file)

            # Récupérer la RAM
            stdin, stdout, stderr = client.exec_command("free -m")
            ram_info = stdout.read().decode().splitlines()[1].split()
            total_ram = int(ram_info[1])  # RAM totale (en MB)
            used_ram = int(ram_info[2])  # RAM utilisée (en MB)
            ram_usage = (used_ram / total_ram) * 100
            ram = f"{used_ram} MB"

            # Récupérer le CPU
            stdin, stdout, stderr = client.exec_command("top -bn1 | grep 'Cpu(s)'")
            cpu_info = stdout.read().decode().splitlines()[0].split(',')
            cpu_usage_str = cpu_info[0].split(':')[1].strip().split()[0].replace(',', '.')
            cpu_usage = float(cpu_usage_str)
            cpu = f"{cpu_usage:.0f}%"

            # Récupérer l'état du disque
            stdin, stdout, stderr = client.exec_command("df -h /")
            disk_info = stdout.read().decode().splitlines()[1].split()
            disk_usage = int(disk_info[4][:-1])  # Utilisation du disque en pourcentage
            disk = disk_info[4]  # Utilisation du disque en format texte

            client.close()

            # Vérifier les seuils et envoyer des alertes si nécessaire
            if cpu_usage > CPU_THRESHOLD:
                send_alert_email(SMTP_CONFIG, hostname, cpu, ram, disk)
            if ram_usage > RAM_THRESHOLD:
                send_alert_email(SMTP_CONFIG, hostname, cpu, ram, disk)
            if disk_usage > DISK_THRESHOLD:
                send_alert_email(SMTP_CONFIG, hostname, cpu, ram, disk)

            return cpu, ram, disk

        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'état du système : {e}")
            return None, None, None

def main():
    try:
        # Chargement de la configuration depuis le fichier JSON sans email_config
        with open('ssh_system_status.json', 'r') as f:
            config = json.load(f)

        # Log pour vérifier le contenu du fichier JSON
        #logging.info(f"Configuration chargée : {config}")
        
        # Vérifiez les sections db_config
        db_config = config.get('db_config')

        if not db_config:
            logging.error("La section 'db_config' est manquante ou incorrecte.")
            return
        
        system_status = SystemStatus(db_config)
        system_status.connect_db()
        system_status.cleanup_old_entries()

        # Parcourir les serveurs et vérifier l'état
        for server in config.get('servers', []):
            if 'hostname' in server and 'username' in server and 'key_file' in server:
                # Retirer l'argument smtp_config ici
                cpu, ram, disk = system_status.get_system_status(server['hostname'], server['username'], server['key_file'])
                if cpu and ram and disk:
                    system_status.store_status(server['hostname'], cpu, ram, disk)
            else:
                logging.error(f"Configuration serveur manquante ou incorrecte : {server}")
     
        system_status.close_db()

    except json.JSONDecodeError as json_err:
        logging.error(f"Erreur de décodage du fichier JSON : {json_err}")
    except FileNotFoundError as file_err:
        logging.error(f"Fichier JSON introuvable : {file_err}")
    except Exception as e:
        logging.error(f"Erreur inattendue : {e}")

if __name__ == "__main__":
    main()