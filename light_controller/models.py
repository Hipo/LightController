import json
import settings
import RPi.GPIO as GPIO

from uuid import uuid4
from settings import LAMP_PINS


class Device(object):
    """
    Holds the name of the device.
    """
    name = None

    def __init__(self):
        try:
            with open(settings.DATA_STORAGE_PATH) as data_file:
                data = json.load(data_file)
            self.name = data["name"]
        except:
            self.name = self.create_unique_name()
            self.save()

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        for LAMP_PIN in LAMP_PINS:
            GPIO.setup(LAMP_PIN, GPIO.OUT)

    def create_unique_name(self):
        name = settings.DEVICE_NAME_TEMPLATE % uuid4().hex[:6]
        return name

    def save(self):
        """
        Saves the device information & state
        to the local storage
        """
        print("Saving device information...")

        data = {
            "name": self.name
        }

        with open(settings.DATA_STORAGE_PATH, 'w') as f:
            json.dump(data, f, ensure_ascii=False)
