#!/usr/bin/env python3
import sys
import os
from gtts import gTTS

def txt_to_mp3(txt_path):
    # Vérification du fichier
    if not os.path.exists(txt_path):
        print(f"Erreur : fichier introuvable : {txt_path}")
        return
    
    # Lecture du texte
    with open(txt_path, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("Erreur : le fichier texte est vide.")
        return

    # Construction du chemin mp3 de sortie
    base, _ = os.path.splitext(txt_path)
    mp3_path = base + ".mp3"

    print(f"▶ Génération MP3 : {mp3_path}")

    # Synthèse vocale
    tts = gTTS(text=text, lang="fr")
    tts.save(mp3_path)

    print("✔ Fichier MP3 généré.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python3 txt2mp3.py chemin/vers/fichier.txt")
        sys.exit(1)

    txt_to_mp3(sys.argv[1])
