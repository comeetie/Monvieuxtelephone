#!/usr/bin/env python3
"""
Script Python pour récupérer les prochains passages d'un arrêt via l'API PRIM / Navitia
et les annoncer avec gTTS.
./prochain_passage_rt.py STIF:StopArea:SP:68653: STIF:Line::C01730: # esbly ligne P
./prochain_passage_rt.py STIF:StopArea:SP:68653: STIF:Line::C02732: # esbly tramway
./prochain_passage_rt.py STIF:StopArea:SP:68578: # coupvray mairie Bus ne marche pas ...
./prochain_passage_rt.py STIF:StopArea:SP:68385: STIF:Line::C01742: # RER A 
A regarder aussi https://prim.iledefrance-mobilites.fr/marketplace/disruptions_bulk/disruptions/v2

"""

import requests
from datetime import datetime
from gtts import gTTS
import subprocess
from urllib.parse import quote
import sys
import argparse
import pytz

# ---------------- CONFIGURATION ----------------
API_KEY = "XX"
# ------------------------------------------------


def get_next_departures(monitoring_ref, line_ref=None):
    url = "https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring"

    headers = {"apikey": API_KEY}

    params = {
        "MonitoringRef": monitoring_ref #"STIF:StopArea:SP:68653:" #quote(monitoring_ref,safe="")
    }
    if line_ref:    
        params["LineRef"] = line_ref # STIF:Line::C01730:"
    response = requests.get(url, headers=headers, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    return(data)


def speak(text):
    tts = gTTS(text, lang="fr")
    audio_file = "prochain_passage.mp3"
    tts.save(audio_file)

    try:
        subprocess.run(["mpg123", "-q", audio_file], check=True)
    except FileNotFoundError:
        print("Erreur : mpg123 non installé. Installer avec : sudo apt install mpg123")


def format_departures(data, max_count=3):
    """
    Retourne une phrase du type :
    "Prochains départs d'Esbly : - 14h55 en direction de Gare de l'Est, - 15h32 en direction de Meaux"
    """
    try:
        visits = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
    except (KeyError, IndexError, TypeError):
        return "Aucune information de passage disponible."

    if not visits:
        return "Aucun prochain passage n’est disponible."

    paris_tz = pytz.timezone("Europe/Paris")

    # ----- Récupération nom de l'arrêt -----
    try:
        first_call = visits[0]["MonitoredVehicleJourney"]["MonitoredCall"]
        stop_name = first_call["StopPointName"][0]["value"]
    except Exception:
        stop_name = "cet arrêt"

    entries = []

    for visit in visits[:max_count]:
        mvj = visit["MonitoredVehicleJourney"]
        call = mvj["MonitoredCall"]

        # Destination
        if call.get("DestinationDisplay"):
            destination = call["DestinationDisplay"][0]["value"]
        else:
            destination = mvj["DestinationName"][0]["value"]

        # Heure de départ
        raw_time = call.get("ExpectedDepartureTime") or call.get("AimedDepartureTime")

        if raw_time:
            dt = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
            dt_fr = dt.astimezone(paris_tz)
            heure = dt_fr.strftime("%Hh%M")
            entries.append(f"- {heure} en direction de {destination}")

    # suppression doublons evts 
    entries= list(dict.fromkeys(entries))

    # Construction de la phrase finale
    final_sentence = f"Prochains départs à {stop_name} : " + "; ".join(entries)
    return final_sentence

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
        departures = get_next_departures(stop_id, line_id)
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

    messages = format_departures(departures,max_count=count)
    print(messages)
    speak(messages)


if __name__ == "__main__":
    main()

