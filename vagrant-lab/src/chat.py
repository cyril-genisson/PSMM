#!/usr/bin/env python3
import requests
import json

# URL du webhook (à remplacer par le tien)
webhook_url = 'https://chat.googleapis.com/v1/spaces/AAAAuish3og/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=sycpUxXD0eIEKZL6xCV4jEamaw8tpgeS5fB25ehgv6k'

# Corps du message (texte simple)
message = {
    "text": "Je suis non sécurisé, non scalable et j'en passe. Tu ne peux me connaître que par l'ensemble \
            des défauts qui me compose. Je suis, je suis... Le WEBHOOK bien sûr!!! \
            Pas très cyber tout cela!!!"
}

# Envoyer le message via une requête POST
headers = {'Content-Type': 'application/json; charset=UTF-8'}
response = requests.post(webhook_url, headers=headers, data=json.dumps(message))

# Vérifier la réponse
if response.status_code == 200:
    print("Message envoyé avec succès.")
else:
    print(f"Erreur {response.status_code}: {response.text}")

