#!/usr/bin/env python3
from datetime import datetime
from gtts import gTTS
import subprocess

def main():
    # Récupère l’heure actuelle
    maintenant = datetime.now()
    heure_str = maintenant.strftime("Il est %H heures %M minutes.")

    # Génère le fichier audio avec gTTS
    tts = gTTS(heure_str, lang="fr")
    audio_file = "heure.mp3"
    tts.save(audio_file)

    # Lecture audio avec subprocess
    try:
        subprocess.run(["mpg123", audio_file], check=True)
    except FileNotFoundError:
        print("Erreur : mpg123 n'est pas installé.")
        print("Installe-le avec : sudo apt install mpg123")

if __name__ == "__main__":
    main()
