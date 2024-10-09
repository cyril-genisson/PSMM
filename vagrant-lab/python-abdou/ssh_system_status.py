import paramiko
import json
import mysql.connector
import logging
from datetime import datetime, timedelta

# Configuration du système de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        """Supprime les entrées de plus de 72 heures."""
        try:
            cutoff_time = datetime.now() - timedelta(hours=72)
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
            ram = f"{ram_info[1]} MB"

            # Récupérer le CPU
            stdin, stdout, stderr = client.exec_command("top -bn1 | grep 'Cpu(s)'")
            cpu_info = stdout.read().decode().splitlines()[0].split(',')
            cpu = cpu_info[0].split(':')[1].strip().split()[0] + '%'  # Formatage correct


            # Récupérer l'état du disque
            stdin, stdout, stderr = client.exec_command("df -h /")
            disk_info = stdout.read().decode().splitlines()[1].split()
            disk = disk_info[4]

            client.close()
            return cpu, ram, disk
        except Exception as e:
            logging.error(f"Erreur lors de la récupération de l'état du système : {e}")
            return None, None, None

def main():
    try:
        # Chargement de la configuration depuis le fichier JSON
        with open('system_status.json', 'r') as f:
            config = json.load(f)

        db_config = config['db_config']  # Utilisation de la configuration unique de la base de données

        # Connexion à la base de données
        system_status = SystemStatus(db_config)
        system_status.connect_db()
        system_status.cleanup_old_entries()  # Nettoyage des anciennes entrées

        # Récupération des données des serveurs
        for server in config['servers']:
            cpu, ram, disk = system_status.get_system_status(server['hostname'], server['username'], server['key_file'])
            if cpu and ram and disk:
                system_status.store_status(server['hostname'], cpu, ram, disk)  # Stockage des données

        system_status.close_db()  # Fermeture de la connexion à la base de données

    except Exception as e:
        logging.error(f"Erreur : {e}")

if __name__ == "__main__":
    main()