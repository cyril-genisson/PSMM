import paramiko
import json

class SSHMariaDBClient:
    def __init__(self, hostname, username, key_file, sudo_password, mariadb_user, mariadb_password):
        self.hostname = hostname
        self.username = username
        self.key_file = key_file
        self.sudo_password = sudo_password
        self.mariadb_user = mariadb_user
        self.mariadb_password = mariadb_password
        self.client = None

    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, username=self.username, key_filename=self.key_file)
            print("Connexion SSH réussie !")
        except Exception as e:
            print(f"Erreur lors de la connexion SSH : {e}")

    def execute_command_with_sudo(self, command):
        try:
            # Ouverture du canal interactif avec un pseudo-terminal (PTY)
            transport = self.client.get_transport()
            channel = transport.open_session()
            channel.get_pty()  # Allocation d'un pseudo-terminal (PTY)
            channel.exec_command(f'sudo -S {command}')
            channel.send(f'{self.sudo_password}\n')  # Envoi du mot de passe sudo

            stdout_data = []
            stderr_data = []
            while True:
                if channel.recv_ready():
                    stdout_data.append(channel.recv(1024).decode('utf-8'))
                if channel.recv_stderr_ready():
                    stderr_data.append(channel.recv_stderr(1024).decode('utf-8'))
                if channel.exit_status_ready():
                    break

            stdout_output = ''.join(stdout_data)
            stderr_output = ''.join(stderr_data)

            if stdout_output:
                print("Commande réussie :")
                print(stdout_output)
            if stderr_output:

                print("Erreurs :")
                print(stderr_output)

        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande : {e}")

    def show_databases(self):
        try:
            # Commande pour lister les bases de données
            mariadb_command = f"mariadb -u {self.mariadb_user} -p'{self.mariadb_password}' -e 'SHOW DATABASES;'"

            # Exécution de la commande avec sudo
            self.execute_command_with_sudo(mariadb_command)
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande MariaDB : {e}")

    def close(self):
        if self.client:
            self.client.close()

def main():
    try:
        # Lecture du fichier de configuration
        with open('connexion_mysql.json', 'r') as connexion_file:
            config = json.load(connexion_file)
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON : {e}")
        return
    except FileNotFoundError as e:
        print(f"Fichier JSON non trouvé : {e}")
        return

    # Initialisation du client SSH pour MariaDB
    ssh_mariadb_client = SSHMariaDBClient(
        hostname=config['hostname'],
        username=config['username'],
        key_file=config['key_file'],
        sudo_password=config.get('sudo_password', ''),
        mariadb_user=config['mariadb_user'],
        mariadb_password=config['mariadb_password']
    )

    # Connexion SSH et exécution de la commande MariaDB
    ssh_mariadb_client.connect()
    ssh_mariadb_client.show_databases()
    ssh_mariadb_client.close()

if __name__ == "__main__":
    main()