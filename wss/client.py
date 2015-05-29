from ws4py.client.tornadoclient import TornadoWebSocketClient
from tornado import ioloop
import json
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Device(object):

    def prepare(self):
        pass

    @property
    def uuid(self):
        return 'uuid-uuid'

class MyClient(TornadoWebSocketClient):

    def __init__(self, url, device):
        url = url.format(uuid=device.uuid)
        super(MyClient, self).__init__(url, protocols=['http-only', 'chat'])

    def opened(self):
        print "opened connection"
        self.send(json.dumps(dict(
            cmd='hello',
            id=1
        )))

    def cmd_ping(self, data):
        return 'pong'

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

if __name__ == '__main__':
    device = Device()
    device.prepare()

    ws = MyClient('ws://127.0.0.1:8888/wss/device/{uuid}/?token=TOKEN_1234', device=device)
    ws.connect()

    ioloop.IOLoop.instance().start()