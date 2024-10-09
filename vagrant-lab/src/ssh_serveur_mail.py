#!/usr/bin/env python3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ServerMail:
    def __init__(self, jsonfile=None):
        self.credentials = jsonfile
    
    def send_email(self, *args, **kwargs):
        msg = MIMEMultipart()
        msg['From'] = self.credentials['sender']
        msg['To'] = kwargs['recipient']
        msg['Subject'] = kwargs['subject']

        match kwargs['type']:
            case "system":
                msg.attach(MIMEText(self.format_system_body(), 'html'))
            case "logins":
                msg.attach(MIMEText(self.format_login_body(), 'html'))
        
        try:
            server = smtplib.SMTP(self.credentials['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.credentials['sender'], self.credentials['password'])  # Utilisez le mot de passe d'application Gmail
            server.sendmail(self.email_config['sender'], kwargs['recipient'], msg.as_string())
            print("Email envoyé avec succès !")
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email : {e}")
        finally:
            server.quit()

    def format_login_body(self, logins):
        """Formate le corps de l'email au format HTML avec un tableau des logs"""
        body = """
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

        body += """
                    </table>
                </body>
            </html>"""
        
        return body
    
    def format_system_login(**kwargs):
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
                    <h2>Alerte de système pour le serveur {kwargs['host']}</h2>
                    <table>
                        <tr>
                            <th>Ressource</th>
                            <th>Utilisation</th>
                        </tr>
                        <tr>
                            <td>Utilisation CPU</td>
                            <td>{kwargs['cpu']}</td>
                        </tr>
                        <tr>
                            <td>Utilisation RAM</td>
                            <td>{kwargs['ram']}</td>
                        </tr>
                        <tr>
                            <td>Utilisation Disque</td>
                            <td>{kwargs['disk']}</td>
                        </tr>
                    </table>
                </body>
                </html>
                """
        return body
    