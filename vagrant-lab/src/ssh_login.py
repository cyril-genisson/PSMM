#!/usr/bin/env python3
import paramiko


class SSHConnection:
    def __init__(self, hostname, port=22, username=None, password=None, key_filename=None, use_ssh_agent=False):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.use_ssh_agent = use_ssh_agent

    def connect(self):
        try:
            if self.use_ssh_agent:
                # Connexion avec une clé de l'agent SSH
                agent = paramiko.Agent()
                keys = agent.get_keys()
                if keys:
                    self.ssh_client.connect(self.hostname, self.port, self.username, pkey=keys[0]) 
                else:
                    raise Exception("Aucune clé trouvée dans l'agent SSH")
            elif self.key_filename:
                # Connexion avec une clé RSA depuis un fichier
                key = paramiko.Ed25519Key.from_private_key_file(self.key_filename)
                self.ssh_client.connect(self.hostname, self.port, self.username, pkey=key)
            else:
                # Connexion avec un mot de passe (si aucune clé n'est fournie)
                self.ssh_client.connect(self.hostname, self.port, self.username, self.password)
            print("Connexion SSH établie avec succès !")
        except Exception as e:
            print(f"Erreur lors de la connexion SSH : {e}")

    def exec_command(self, command):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            output = stdout.read().decode()
            errors = stderr.read().decode()
            if errors:
                print(f"Erreur lors de l'exécution de la commande : {errors}")
            print(output)
            return command, output, errors
        except Exception as e:
            print(f"Exception : {e}")
            return None

    def close(self):
        self.ssh_client.close()


if __name__ == "__main__":
    print()
    