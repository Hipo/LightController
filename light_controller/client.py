from ws4py.client.tornadoclient import TornadoWebSocketClient
from tornado import ioloop

import json
import logging
import signal

try:
    import RPi.GPIO as GPIO
except:
    print("RPI IMPORT ERROR!!!!")

    class GPIO(object):
        @classmethod
        def setwarnings(cls, *args, **kwargs):
            pass

        @classmethod
        def setmode(cls, *args, **kwargs):
            pass

        @classmethod
        def setup(cls, *args, **kwargs):
            pass

        @classmethod
        def output(cls, *args, **kwargs):
            pass


        BCM = None
        OUT = None
        LOW = None
        HIGH = None

from models import Device
from settings import LAMPS


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class MyClient(TornadoWebSocketClient):
    def __init__(self, url, device):
        url = url.format(name=device.name)
        super(MyClient, self).__init__(url, protocols=['http-only', 'chat'])

    def opened(self):
        print "opened connection"
        print LAMPS.keys()
        self.send(json.dumps(dict(
            cmd='hello',
            switches=LAMPS.keys(),
            id=1
        )))

    def cmd_ping(self, data):
        return 'pong'

    def cmd_switch_light(self, data):
        switch_id = data["switch_id"]
        on_off = data["on_off"] == "True"

        print "here i switch %s to %s" % (switch_id, on_off)
        GPIO.output(LAMPS[switch_id], GPIO.LOW if on_off else GPIO.HIGH)

    def received_message(self, m):
        try:
            msg = json.loads(m.data)
            print "received message", msg
            cmd = msg.get('cmd', None)
            if cmd:
                fn = getattr(self, 'cmd_%s' % cmd)
                reply = fn(msg)
                if reply:
                    self.send(json.dumps(dict(
                        reply=reply,
                        id=msg['id']
                    )))

        except:
            logger.exception("exc in receive")

    def closed(self, code, reason=None):
        # TODO: reconnect or reconnect client
        raise Exception('socket closed')
        # ioloop.IOLoop.instance().stop()


def sigterm_handler(_signo, _stack_frame):
    """
    Caught SIGTERM, cleanup and exit
    """
    try:
        GPIO.cleanup()

        sys.exit(0)
    except:
        pass

signal.signal(signal.SIGTERM, sigterm_handler)

import os

if __name__ == '__main__':

    # WS_URL='ws://127.0.0.1:8888/wss/device/{name}/?token=TOKEN_1234' python light_controller/client.py

    try:
        device = Device()

        WS_URL = os.getenv('WS_URL', 'ws://127.0.0.1:8888/wss/device/{name}/?token=TOKEN_1234')

        ws = MyClient(WS_URL, device=device)
        ws.connect()

        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        GPIO.cleanup()
