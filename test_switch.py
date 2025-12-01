#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("GPIO4 diagnostic — open/close the switch")

try:
    while True:
        state = GPIO.input(25)
        print(state)
        print("GPIO4 =", "HIGH" if state else "LOW")
        time.sleep(0.3)
except KeyboardInterrupt:
    GPIO.cleanup()
