import json
import settings
from uuid import uuid4


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

