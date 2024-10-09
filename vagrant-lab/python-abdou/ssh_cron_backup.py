import paramiko
import json
import os
import logging
from datetime import datetime

# Configuration du système de log
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MySQLBackup:
    def __init__(self, mysql_hostname, mysql_user, mysql_password, db_name, backup_dir):
        self.mysql_hostname = mysql_hostname
        self.mysql_user = mysql_user
        self.mysql_password = mysql_password
        self.db_name = db_name
        self.backup_dir = backup_dir
        self.client = None

    def connect_ssh(self, hostname, username, key_file):
        """Connexion SSH au serveur distant."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname, username=username, key_filename=key_file)
            logging.info(f"Connexion SSH réussie sur {hostname}.")
        except Exception as e:
            logging.error(f"Erreur de connexion SSH à {hostname} : {e}")

    def close_ssh(self):
        """Ferme la connexion SSH."""
        if self.client:
            self.client.close()
            logging.info("Connexion SSH fermée.")

    def perform_backup(self):
        """Réalise une sauvegarde de la base de données sur le serveur distant."""
        try:
            # Création du nom de fichier avec horodatage
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            backup_file = f"ssh_access_logs_backup_{timestamp}.sql"

            # Commande de sauvegarde de la base de données
            backup_command = f"mysqldump -u {self.mysql_user} -p{self.mysql_password} {self.db_name} > {self.backup_dir}/{backup_file}"

            # Exécution de la commande de sauvegarde via la connexion SSH
            stdin, stdout, stderr = self.client.exec_command(backup_command)
            exit_status = stdout.channel.recv_exit_status()

            if exit_status == 0:
                logging.info(f"Sauvegarde réussie : {backup_file}")
            else:
                logging.error(f"Erreur lors de la sauvegarde : {stderr.read().decode()}")

        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde : {e}")

    def cleanup_old_backups(self, retention_days=7):
        """Supprime les sauvegardes qui dépassent la durée de rétention."""
        try:
            # Récupère la liste des fichiers de sauvegarde
            backup_list_command = f"ls -t {self.backup_dir}/ssh_access_logs_backup_*.sql"
            stdin, stdout, stderr = self.client.exec_command(backup_list_command)
            backup_files = stdout.read().decode().splitlines()

            # Conserver uniquement les X dernières sauvegardes
            if len(backup_files) > retention_days:
                old_files = backup_files[retention_days:]
                for old_file in old_files:
                    delete_command = f"rm {self.backup_dir}/{os.path.basename(old_file)}"
                    self.client.exec_command(delete_command)
                    logging.info(f"Ancienne sauvegarde supprimée : {old_file}")
        except Exception as e:
            logging.error(f"Erreur lors du nettoyage des anciennes sauvegardes : {e}")

def main():
    try:
        # Chargement de la configuration depuis le fichier JSON
        with open('ssh_cron_backup.json', 'r') as f:
            config = json.load(f)

        backup_client = MySQLBackup(
            mysql_hostname=config['hostname'],
            mysql_user=config['mysql_user'],
            mysql_password=config['mysql_password'],
            db_name=config['db_config']['database'],
            backup_dir=config['backup_dir']
        )

        # Connexion SSH et exécution du processus de sauvegarde
        backup_client.connect_ssh(config['hostname'], config['username'], config['key_file'])
        backup_client.perform_backup()
        backup_client.cleanup_old_backups()
        backup_client.close_ssh()

    except Exception as e:
        logging.error(f"Erreur : {e}")

if __name__ == "__main__":
    main()