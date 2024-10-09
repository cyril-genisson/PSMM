import paramiko
import json

class SSHClient:
    def __init__(self, hostname, username, key_file, sudo_password):
        self.hostname = hostname
        self.username = username
        self.key_file = key_file
        self.sudo_password = sudo_password
        self.client = paramiko.SSHClient()

    def connect(self):
        try:
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, username=self.username, key_filename=self.key_file)
            print("Connexion...")
        except Exception as e:
            print(f"Erreur de connexion : {e}")

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

            output = ''.join(stdout_data)
            error_output = ''.join(stderr_data)
            if output:
                print("Connexion réussie !")
                print(output)
            if error_output:
                print("Erreurs :")
                print(error_output)

            channel.close()
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande : {e}")

    def close(self):
        self.client.close()

def main():
    try:
        with open('connexion.json', 'r') as connexion_file:
            config = json.load(connexion_file)
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON : {e}")
        return
    except FileNotFoundError as e:
        print(f"Fichier JSON non trouvé : {e}")
        return

    ssh_client = SSHClient(
        hostname=config['hostname'],
        username=config['username'],
        key_file=config['key_file'],
        sudo_password=config.get('sudo_password', '')  # Récupère le mot de passe sudo s'il est présent
    )

    ssh_client.connect()
    ssh_client.execute_command_with_sudo(config['command'])
    ssh_client.close()

if __name__ == "__main__":
    main()