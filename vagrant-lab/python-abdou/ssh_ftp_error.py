import paramiko
import re
import mysql.connector
import json


class FTPLogExtractor:
    def __init__(self, hostname, username, key_file, sudo_password, db_config, log_file):
        self.hostname = hostname
        self.username = username
        self.key_file = key_file
        self.sudo_password = sudo_password
        self.db_config = db_config
        self.log_file = log_file
        self.client = None

    def connect_ssh(self):
        """Connecte au serveur SSH."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, username=self.username, key_filename=self.key_file)
            print("Connexion SSH réussie !")
        except Exception as e:
            print(f"Erreur lors de la connexion SSH : {e}")

    def read_log_file(self):
        """Lit le fichier de logs sur le serveur distant."""
        try:
            command = f"cat {self.log_file}"
            transport = self.client.get_transport()
            channel = transport.open_session()
            channel.get_pty()
            channel.exec_command(f'sudo -S {command}')
            channel.send(f'{self.sudo_password}\n')

            output = ''
            error_output = ''
            while True:
                if channel.recv_ready():
                    output += channel.recv(1024).decode('utf-8')
                if channel.recv_stderr_ready():
                    error_output += channel.recv_stderr(1024).decode('utf-8')
                if channel.exit_status_ready():
                    break

            if error_output:
                print("Erreur lors de la lecture des logs :", error_output)
                return None
            #print("Contenu des logs :", output)  # Ajout ici pour voir le contenu des logs
            return output
        
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier log : {e}")
            return None

    def close_ssh(self):
        """Ferme la connexion SSH."""
        if self.client:
            self.client.close()
            print("Connexion SSH fermée.")

    def extract_failed_logins(self, log_data):
        pattern = re.compile(r"(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2}),\d+\s+ServeurFTP proftpd\[\d+\] ServeurFTP \([\d\.]+\[\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\]\): USER (\w+): no such user found from ([\d\.]+)")
        failed_logins = pattern.findall(log_data)

        # Combiner date et heure et réorganiser
        formatted_failed_logins = [(user, ip, f"{date} {time}") for date, time, user, ip in failed_logins]
        
        #print("Tentatives d'accès extraites :", formatted_failed_logins)
        return formatted_failed_logins


    def store_in_db(self, failed_logins):
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()

            for login in failed_logins:
                #print(f"Login extrait : {login}")  # Debug
                if len(login) != 3:
                    print(f"Format inattendu pour login : {login}")
                    continue

                username, ip_address, attempt_time = login
                cursor.execute(
                    "SELECT COUNT(*) FROM failed_logins_ftp WHERE username = %s AND ip_address = %s AND attempt_time = %s",
                    (username, ip_address, attempt_time)
                )
                result = cursor.fetchone()

                if result[0] == 0:
                    print(f"Insertion dans DB : {username}, {ip_address}, {attempt_time}")
                    cursor.execute(
                        "INSERT INTO failed_logins_ftp (username, ip_address, attempt_time) VALUES (%s, %s, %s)",
                        (username, ip_address, attempt_time)
                    )
                else:
                    print(f"Doublon détecté : {username}, {ip_address}, {attempt_time} - Ignoré.")
            
            connection.commit()
            print("Logs insérés dans la base de données avec succès !")

        except mysql.connector.Error as e:
            print(f"Erreur MySQL : {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

def main():
    try:
        with open('ssh_ftp_error.json', 'r') as f:
            config = json.load(f)

        ftp_client = FTPLogExtractor(
            hostname=config['hostname'],
            username=config['username'],
            key_file=config['key_file'],
            sudo_password=config['sudo_password'],
            db_config=config['db_config'],
            log_file=config['log_file']
        )

        ftp_client.connect_ssh()

        log_data = ftp_client.read_log_file()
        if log_data:
            failed_logins = ftp_client.extract_failed_logins(log_data)
            ftp_client.store_in_db(failed_logins)

        ftp_client.close_ssh()

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()