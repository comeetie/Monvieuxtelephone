#!/usr/bin/env python3
import requests
from gtts import gTTS
import os

BASE_DIR = "/home/comeetie/Stories/1/"

def get_weather_text(day_offset=0):
    LAT, LON = 48.869, 2.775
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=Europe/Paris"
    resp = requests.get(url, timeout=5).json()
    temps_max = int(resp["daily"]["temperature_2m_max"][day_offset])
    temps_min = int(resp["daily"]["temperature_2m_min"][day_offset])
    weather_code = resp["daily"]["weathercode"][day_offset]
    codes = {0: "ciel dégagé",1: "principalement dégagé",2: "partiellement nuageux",3: "couvert",45: "brume",48: "brume givrée",51: "bruine légère",53: "bruine modérée",55: "bruine dense", 56: "bruine glaciale légère", 57: "bruine glaciale dense",61: "pluie légère",63: "pluie modérée",65: "pluie forte",66: "pluie verglaçante légère",67: "pluie verglaçante forte",71: "neige légère",73: "neige modérée",75: "neige forte",77: "grésil",80: "averses de pluie légères",81: "averses de pluie modérées",82: "averses de pluie fortes",85: "averses de neige légères",86: "averses de neige fortes",95: "orage",96: "orage avec grêle légère",99: "orage avec grêle forte"}
    desc = codes.get(weather_code,"temps inconnu")
    prefix = {0:"Aujourd'hui",1:"Demain",2:"Surlendemain"}.get(day_offset,"Météo")
    return f"{prefix} à Coupvray : {desc}, entre {temps_min} et {temps_max} degrés."

def generate_mp3(filename, text):
    path = os.path.join(BASE_DIR, filename)
    tts = gTTS(text=text, lang='fr')
    tts.save(path)
    print("MP3 généré :", path)

# --- génération ---
generate_mp3("0.mp3", get_weather_text(0))
generate_mp3("1.mp3", get_weather_text(0))  # tu peux ajouter plus de détails si tu veux
generate_mp3("2.mp3", get_weather_text(1))
generate_mp3("3.mp3", get_weather_text(2))
