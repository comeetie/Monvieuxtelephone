#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

PIN = 17   # ton entrée GPIO

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    logf = open("rotary_raw.log", "w")

    print("=== Analyse brute du cadran rotatif ===")
    print("Tourne un chiffre et observe les impulsions...")
    print("Chaque ligne = un front détecté (montant/descendant)")
    print("Ctrl+C pour arrêter\n")

    last_time = time.time()

    def callback(channel):
        nonlocal last_time

        now = time.time()
        delta = (now - last_time) * 1000.0  # en ms
        last_time = now

        state = GPIO.input(PIN)

        msg = f"{now:.6f}|{'HIGH' if state else 'LOW'}|{delta:.1f}"
        print(msg)
        logf.write(msg + "\n")
        logf.flush()

    # on écoute rising
    GPIO.add_event_detect(PIN, GPIO.BOTH, callback=callback, bouncetime=10)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        logf.close()
        GPIO.cleanup()
        print("\nFin de l'analyse. Fichier écrit : rotary_raw.log")

if __name__ == "__main__":
    main()
