import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

class SshServeurMail:
    def __init__(self, db_config, email_config):
        self.db_config = db_config
        self.email_config = email_config

    def get_failed_logins_yesterday(self):
        """Récupère les tentatives de connexion échouées depuis les dernières 48 heures depuis la base de données"""
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()

            # Requête SQL pour récupérer les logs des dernières 48 heures
            query = """
            SELECT username, ip_address, attempt_time
            FROM failed_logins_web
            WHERE attempt_time >= NOW() - INTERVAL 2 DAY;
            """  # Modifié pour les dernières 48 heures (2 jours)
            cursor.execute(query)
            failed_logins = cursor.fetchall()
            print(failed_logins)

            if not failed_logins:
                return None
            
            return failed_logins

        except mysql.connector.Error as e:
            print(f"Erreur MySQL : {e}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def send_email(self, logins):
        """Envoie un email à l'administrateur avec les logs des tentatives de connexion au format HTML"""
        msg = MIMEMultipart()
        msg['From'] = self.email_config['sender']
        msg['To'] = self.email_config['recipient']
        msg['Subject'] = "Historique des tentatives de connexion échouées (Dernières 48 heures)"

        # Corps de l'e-mail avec format HTML
        msg.attach(MIMEText(self.format_email_body(logins), 'html'))

        # Connexion au serveur SMTP de Gmail
        try:
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['sender'], self.email_config['password'])  # Utilisez le mot de passe d'application Gmail
            server.sendmail(self.email_config['sender'], self.email_config['recipient'], msg.as_string())
            print("Email envoyé avec succès !")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")
        finally:
            server.quit()

    def format_email_body(self, logins):
        """Formate le corps de l'email au format HTML avec un tableau des logs"""
        body = """\
        <html>
            <head>
                <style>
                    table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    table, th, td {
                        border: 1px solid black;
                    }
                    th, td {
                        padding: 8px;
                        text-align: left;
                    }
                    th {
                        background-color: #f2f2f2;
                    }
                </style>
            </head>
            <body>
                <h2>Historique des tentatives de connexion échouées</h2>
                <p>Voici les tentatives de connexion échouées des dernières 48 heures :</p>
                <table>
                    <tr>
                        <th>Username</th>
                        <th>IP address</th>
                        <th>Attempt Time</th>
                    </tr>"""

        for login in logins:
            username, ip_address, attempt_time = login
            body += f"""
                    <tr>
                        <td>{username}</td>
                        <td>{ip_address}</td>
                        <td>{attempt_time}</td>
                    </tr>"""

        body += """\
                </table>
            </body>
        </html>"""
        
        return body

    def run(self):
        failed_logins = self.get_failed_logins_yesterday()  # Récupère les logs des dernières 48 heures

        if not failed_logins:
            print("Aucune tentative de connexion échouée dans les dernières 48 heures.")
        else:
            print("Tentatives échouées récupérées, envoi de l'email...")
            self.send_email(failed_logins)


if __name__ == "__main__":
    # Charger les configurations depuis le fichier JSON
    with open('ssh_serveur_mail.json', 'r') as config_file:
        config = json.load(config_file)

    db_config = config['db_config']
    email_config = config['email_config']
    
    # Lancer le script
    ssh_mailer = SshServeurMail(db_config, email_config)
    ssh_mailer.run()