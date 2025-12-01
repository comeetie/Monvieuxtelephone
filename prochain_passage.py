#!/usr/bin/env python3
"""
Script Python pour récupérer les prochains passages d'un arrêt via l'API PRIM / Navitia
et les annoncer avec gTTS.
"""

import requests
from datetime import datetime
from gtts import gTTS
import subprocess
from urllib.parse import quote
import sys
import argparse

# ---------------- CONFIGURATION ----------------
API_KEY = "XX"
# ------------------------------------------------


def get_next_departures(stop_id, line_id=None, count=3):
    stop_id_enc = quote(stop_id, safe="")
    url = f"https://prim.iledefrance-mobilites.fr/marketplace/v2/navitia/stop_areas/{stop_id_enc}/departures"

    headers = {"apikey": API_KEY}
    params = {"count": count}

    if line_id:
        params["lines"] = quote(line_id, safe="")

    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json().get("departures", [])


def speak(text):
    tts = gTTS(text, lang="fr")
    audio_file = "prochain_passage.mp3"
    tts.save(audio_file)

    try:
        subprocess.run(["mpg123", "-q", audio_file], check=True)
    except FileNotFoundError:
        print("Erreur : mpg123 non installé. Installer avec : sudo apt install mpg123")


def format_departure(dep):
    info = dep.get("display_informations", {})
    dt_raw = dep["stop_date_time"]["departure_date_time"]
    dt = datetime.strptime(dt_raw, "%Y%m%dT%H%M%S")
    heure = dt.strftime("%H:%M")

    ligne = info.get("code", "???")
    dest = info.get("direction", "Destination inconnue")

    return f"Ligne {ligne} direction {dest} à {heure}"


def main():
    parser = argparse.ArgumentParser(description="Annoncer les prochains passages à un arrêt IDFM.")

    parser.add_argument("stop_id", help="Identifiant stop_area ou stop_point")
    parser.add_argument("line_id", nargs="?", default=None, help="Identifiant de la ligne (optionnel)")
    parser.add_argument("count", nargs="?", default=3, type=int, help="Nombre de passages à annoncer")

    args = parser.parse_args()

    stop_id = args.stop_id
    line_id = args.line_id if args.line_id not in ("", "None") else None
    count = args.count

    try:
        departures = get_next_departures(stop_id, line_id, count)
    except requests.HTTPError as e:
        print(f"Erreur HTTP : {e}")
        return
    except requests.RequestException as e:
        print(f"Erreur réseau : {e}")
        return

    if not departures:
        msg = "Aucun passage trouvé pour cet arrêt."
        print(msg)
        speak(msg)
        return

    messages = []
    for dep in departures:
        msg = format_departure(dep)
        print(msg)
        messages.append(msg)

    speak("Voici les prochains passages : " + ". ".join(messages))


if __name__ == "__main__":
    main()

