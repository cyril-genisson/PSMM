import requests
from requests.exceptions import RequestException
import urllib3
import re

# Désactiver les avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Fonction pour obtenir le challenge depuis l'URL d'authentification
def get_challenge():
    url = "http://wonderfulfunsublimemorning.neverssl.com/online"
    
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            print("Page d'authentification récupérée.")
            # Extraction du challenge à partir de l'HTML
            match = re.search(r'name="challenge" value="([^"]+)"', response.text)
            if match:
                challenge = match.group(1)
                print(f"Challenge extrait : {challenge}")
                return challenge
            else:
                print("Challenge non trouvé dans la page.")
                return None
        else:
            print(f"Erreur lors de la récupération de la page : Statut {response.status_code}")
            return None

    except RequestException as e:
        print(f"Erreur lors de la requête : {e}")
        return None

# Fonction pour se connecter à l'URL d'authentification
def login_to_authentication_site(username, password):
    challenge = get_challenge()
    if challenge is None:
        print("Impossible d'obtenir le challenge.")
        return

    login_url = "https://alcasar.laplateforme.io/intercept.php"  # Utilise l'URL Alcasar correcte ici
    
    # Données du formulaire à envoyer avec la requête POST
    data = {
        'username': username,
        'password': password,
        'challenge': challenge,
        'button': 'Authentication'  # Ce champ simule le clic sur le bouton
    }

    try:
        # Envoie de la requête POST avec les données d'authentification
        response = requests.post(login_url, data=data, verify=False, timeout=10)
        if response.status_code == 200:
            print("Bienvenue abdou.rachidou-arouna@laplateforme.io\nAuthentification réussie !")
            #print(f"Contenu de la réponse : {response.text}")
        else:
            print(f"Erreur lors de la connexion: Statut {response.status_code}")
            print(f"Contenu de la réponse : {response.text}")

    except RequestException as e:
        print(f"Erreur lors de la requête de connexion : {e}")

# Informations de connexion insérées directement dans le script
username = "email ou identifiant"
password = "Mot de passe"  # Remplacer par le mot de passe correct

# Exécuter la fonction de connexion
login_to_authentication_site(username, password)