#!/usr/bin/env python3
from ssh_login import SSHConnection
import time


class SSHConnectionWithSudo(SSHConnection):
    def __init__(self, hostname, port=22, username=None, password=None, key_filename=None,
                 use_ssh_agent=False):
        super().__init__(hostname, port, username, password, key_filename, use_ssh_agent)


    def exec_sudo_command(self, command):
        try:
            sudo_command = f'sudo -S {command}'

            stdin, stdout, stderr = self.ssh_client.exec_command(sudo_command, get_pty=True) 

            # Récupération de la sortie et des erreurs
            output = stdout.read().decode()
            errors = stderr.read().decode()

            if errors:
                print(f"Erreur lors de l'exécution de la commande sudo : {errors}")
            return output
        
        except Exception as e:
            print(f"Erreur lors de l'exécution de la commande sudo : {e}")
            return None


if __name__ == "__main__":
    print()
