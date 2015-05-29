#!/usr/bin/env python

import RPi.GPIO as GPIO

from time import sleep


# GPIO pins (BCM numbering)
LAMP2_PIN = 14
BUTTON_PIN = 15


def init_pins():
    """
    Initialize pin modes
    """
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LAMP2_PIN, GPIO.OUT)


def cleanup_pins():
    """
    Cleanup pin states on GPIO
    """
    GPIO.cleanup()


def sigterm_handler(_signo, _stack_frame):
    """
    Caught SIGTERM, cleanup and exit
    """
    cleanup_pins()
    sys.exit(0)


signal.signal(signal.SIGTERM, sigterm_handler)


if __name__ == "__main__":
    init_pins()

    try:
        while True:
            if GPIO.input(BUTTON_PIN) == True:
                GPIO.output(LAMP2_PIN, GPIO.LOW)
            else:
                GPIO.output(LAMP2_PIN, GPIO.HIGH)

            sleep(1.0)

    except KeyboardInterrupt:
        cleanup_pins()
