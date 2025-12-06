#!/usr/bin/env python3
import time
import os
import subprocess
import RPi.GPIO as GPIO
import threading


# ===================== CONSTANTES =====================
PULSE_TIMEOUT = 0.600
COMPOSE_TIMEOUT = 2.500

PIN_PULSE = 17
PIN_HOOK = 25

BASE_DIR = "/home/comeetie/Stories"  # doit contenir oli/, frisson/, histoires/, meteo/
TONE_FILE = os.path.join(BASE_DIR, "tone_la.mp3")  # MP3 tonalité continue

VOLUME = 20000  # volume pour mpg123 (-f)
DEBUG = True

prefix = ""


# ===================== DEBUG =====================
def dbg(*args):
    if DEBUG:
        print("[DEBUG]", *args)

# ===================== TONALITÉ =====================
tone_process = None
audio_playing = False  # True si un son (histoire ou météo) est en cours

# ===================== PLAY / PAUSE =====================
mpg123_control = None

def start_tone():
    global tone_process
    if audio_playing or tone_process:
        dbg("Lecture en cours, tonalité non lancée")
        return
    tone_process = subprocess.Popen(["mpg123", "-m", "-f", str(VOLUME), "--loop", "-1", TONE_FILE])
    dbg("Tonalité start")

def stop_tone():
    global tone_process
    if tone_process:
        tone_process.terminate()
        tone_process = None
        dbg("Tonalité stop")

# ===================== ROTARY =====================
class Rotary:
    def __init__(self):
        self.value = ""
        self.pulse_count = 0
        self.pulse_timer = None
        self.compose_timer = None
        self.on_composition_start = None
        self.on_composition_end = None

    def _cancel(self, timer):
        if timer: timer.cancel()

    def on_pulse(self):
        dbg("Impulsion reçue")
        if self.pulse_count == 0 and self.on_composition_start:
            self.on_composition_start()
        self.pulse_count += 1
        dbg("+1 impulsion, pulse_count =", self.pulse_count)
        self._cancel(self.pulse_timer)
        self._cancel(self.compose_timer)
        self.pulse_timer = threading.Timer(PULSE_TIMEOUT, self._pulse_timeout)
        self.pulse_timer.start()

    def _pulse_timeout(self):
        num = (self.pulse_count //2) % 10
        dbg("Fin chiffre :", num)
        self.value += str(num)
        self.pulse_count = 0
        self.compose_timer = threading.Timer(COMPOSE_TIMEOUT, self._compose_timeout)
        self.compose_timer.start()

    def _compose_timeout(self):
        dbg("Fin composition :", self.value)
        if self.on_composition_end:
            self.on_composition_end(self.value)
        self.value = ""
        self.pulse_count = 0

# ===================== AUDIO =====================
def play_audio(path):
    global audio_playing
    global mpg123_control
    dbg("Lecture audio :", path)
    audio_playing = True
    mpg123_control, slave = os.openpty()
    process = subprocess.Popen(["mpg123", "-C","-m", "-f", str(VOLUME), path],stdin=mpg123_control)
    process.wait()
    audio_playing = False
    mpg123_control = None
    start_tone()

def stop_audio():
    global audio_playing
    dbg("Arrêt audio")
    subprocess.call(["pkill", "mpg123"])
    mpg123_control = None
    audio_playing = False


# ===================== PYTHON SCRIPT =====================
def run_python(path):
    global audio_playing
    dbg("Run python :", path)
    audio_playing = True
    process = subprocess.Popen(["python3", path])
    process.wait()
    audio_playing = False
    start_tone()

# ===================== PATH =====================
def resolve_path(num):
    global prefix

    digits = prefix + num
    path_parts = list(digits)

    current = BASE_DIR
    i = 0

    # 1) Descente dans les dossiers tant qu'ils existent
    while i < len(path_parts):
        next_path = os.path.join(current, path_parts[i])
        if os.path.isdir(next_path):
            current = next_path
            i += 1
        else:
            break  # STOP dès qu'on ne trouve plus de dossier

    # 2) Reste du numéro = nom du fichier potentiel
    file_digits = path_parts[i:]
    filename = "".join(file_digits)


    mp3_path = os.path.join(current, filename + ".mp3")
    py_path  = os.path.join(current, filename + ".py")
    folder_path = os.path.join(current, filename)

    if (filename == "") and os.path.isdir(folder_path):
        return ("dir", None, folder_path)

    if os.path.exists(mp3_path):
        return ("mp3", mp3_path, None)

    if os.path.exists(py_path):
        return ("py", py_path, None)

    return None

# ===================== HISTOIRES =====================
def play_story(number):
    if audio_playing and mpg123_control and number=="0" : 
        dbg("Mise en pause")
        os.write(mpg123_control, b's')
        
    if audio_playing:
        dbg("Lecture en cours, histoire non lancée")
        return
    dbg("Lecture de :"+number)    
   
    global prefix

    result = resolve_path(number)

    if not result:
        dbg("Numéro inconnu.")
        play_audio(os.path.join(BASE_DIR, "notfound.mp3"))
        start_tone()
        return 

    rtype, file_path, folder_path = result

    if rtype == "mp3":
        dbg("Lecture histoire :", file_path)
        play_audio(file_path)
        return

    if rtype == "py":
        dbg("run python script",file_path)
        run_python(file_path)
        return

    if rtype == "dir":
        desc = os.path.join(folder_path, "description.mp3")
        if os.path.exists(desc):
            play_audio(desc)
        prefix = prefix + number
        return
   

# ===================== HOOK =====================
def on_hook_event(channel):
    state = GPIO.input(PIN_HOOK)
    if state == 0:   # décroché
        print("📞 Décroché")
        start_tone()
    else:            # raccroché
        print("📞 Raccroché → arrêt audio & tonalité")
        global prefix
        prefix = ""
        stop_tone()
        stop_audio()

# ===================== MAIN =====================
def main():
    print("=== Story Phone ===")
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_PULSE, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(PIN_HOOK, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    rotary = Rotary()

    def handle_start():
        print("[ROTARY] Début de composition")
        stop_tone()  # arrêt tonalité, ne relance pas
        dbg("handle_start appelé")

    def handle_end(number):
        print("[ROTARY] Numéro :", number)
        stop_tone()  # arrêt tonalité si encore active
        dbg("handle_end appelé avec", number)

        # --- HISTOIRES ---
        play_story(number)

    rotary.on_composition_start = handle_start
    rotary.on_composition_end = handle_end

    GPIO.add_event_detect(PIN_PULSE, GPIO.BOTH, callback=lambda ch: rotary.on_pulse(), bouncetime=10)
    GPIO.add_event_detect(PIN_HOOK, GPIO.BOTH, callback=on_hook_event, bouncetime=100)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
        print("Bye !")

if __name__ == "__main__":
    main()

