#!/usr/bin/env python3
from gtts import gTTS
import subprocess
import tempfile

# --- Texte à transformer en parole ---
text = "Désolé la ligne est occupée, je n'ai pas pu joindre votre correspondant !"

# --- Créer un fichier MP3 temporaire ---
with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
    mp3_path = f.name

# --- Générer le MP3 ---
tts = gTTS(text=text, lang='fr',tld = 'ca')
tts.save(mp3_path)

print("MP3 généré :", mp3_path)

# --- Lire le MP3 ---
subprocess.call(["mpg123", mp3_path])
