import paramiko
import json

class SSHClient:
    def __init__(self, hostname, username, key_file):
        self.hostname = hostname
        self.username = username
        self.key_file = key_file
        self.client = paramiko.SSHClient()

    def connect(self):
        try:
            # Ajouter la politique pour accepter les clés d'hôtes manquantes
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # Connexion au serveur SSH
            self.client.connect(self.hostname, username=self.username, key_filename=self.key_file)
            print("Connexion... !")
        except Exception as e:
            print(f"Erreur de connexion : {e}")

    def execute_command(self, command):
        try:
            # Exécution de la commande distante
            stdin, stdout, stderr = self.client.exec_command(command)
            # Affichage de la sortie de la commande
            output = stdout.read().decode('utf-8')
            error_output = stderr.read().decode('utf-8')
            if output:
                print("Connexion réussie !")
                print(output)
            if error_output:
                print("Erreurs :")
                print(error_output)
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande : {e}")

    def close(self):
        # Fermeture de la connexion SSH
        self.client.close()

def main():
    # Lecture des informations de connexion à partir du fichier JSON
    with open('connexion.json', 'r') as connexion_file:
        config = json.load(connexion_file)

    # Création de l'objet SSHClient
    ssh_client = SSHClient(
        hostname=config['hostname'],
        username=config['username'],
        key_file=config['key_file']
    )

    # Connexion et exécution de la commande
    ssh_client.connect()
    ssh_client.execute_command(config['command'])
    ssh_client.close()

if __name__ == "__main__":
    main()