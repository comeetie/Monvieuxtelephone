#!/usr/bin/env python3
import threading
import time
import RPi.GPIO as GPIO

# --- CONSTANTES ---
PULSE_TIMEOUT = 0.600      # 500 ms entre impulsions d'un même chiffre
COMPOSE_TIMEOUT = 2.5000    # 2000 ms entre deux chiffres = fin de composition
PIN = 17

# --- CLASSE ROTARY ---
class Rotary:
    def __init__(self):
        self.value = ""
        self.pulse_count = 0
        self.pulse_timer = None
        self.compose_timer = None

        self.on_composition_start = None
        self.on_composition_end = None

    def _cancel(self, timer):
        if timer is not None:
            timer.cancel()

    def on_pulse(self):
        """Appelé à chaque impulsion du cadran rotatif."""
        if self.pulse_count == 0 and self.on_composition_start:
            self.on_composition_start()

        self.pulse_count += 1
        print("+1")
        # reset timers
        self._cancel(self.pulse_timer)
        self._cancel(self.compose_timer)

        # timer fin d'un chiffre
        self.pulse_timer = threading.Timer(PULSE_TIMEOUT, self._pulse_timeout)
        self.pulse_timer.start()

    def _pulse_timeout(self):
        """Fin des impulsions d’un chiffre."""
        num = (self.pulse_count // 2) %10  
        self.value += str(num)
        self.pulse_count = 0

        # timer fin de composition totale
        self.compose_timer = threading.Timer(COMPOSE_TIMEOUT, self._compose_timeout)
        self.compose_timer.start()

    def _compose_timeout(self):
        """Fin du numéro complet."""
        if self.on_composition_end:
            self.on_composition_end(self.value)

        self.value = ""
        self.pulse_count = 0


# --- PROGRAMME PRINCIPAL ---
def main():
    print("=== Rotary Dial Listener ===")
    print("En attente des impulsions... (Ctrl+C pour quitter)")

    rotary = Rotary()

    # callbacks
    def handle_start():
        print("[ROTARY] Début de composition")

    def handle_end(number):
        print(f"[ROTARY] Numéro composé : {number}")
        # → ici, tu peux faire ce que tu veux avec le numéro

    rotary.on_composition_start = handle_start
    rotary.on_composition_end = handle_end

    # Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Fonction appelée à chaque impulsion
    def gpio_pulse(channel):
        rotary.on_pulse()

    GPIO.add_event_detect(PIN, GPIO.BOTH, callback=gpio_pulse, bouncetime=10)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nArrêt demandé. Nettoyage GPIO...")
        GPIO.cleanup()
        print("Terminé.")


if __name__ == "__main__":
    main()
