import websocket
import unittest
from multiprocessing import Process
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import time
import os
import json
import requests
import wss
import json
import os


class TestChat(unittest.TestCase):

    def setUp(self):
        self.process = Process(target=wss.run)
        self.process.start()

        time.sleep(2)

    def test_client(self):
        ws = websocket.create_connection("ws://127.0.0.1:8888/wss/device/UUID-12345/?token=TOKEN_1234")

        time.sleep(1)
        d = json.dumps(dict(
            cmd="hello",
            type="message",
            id=1

        ))
        ws.send(d)

        result = ws.recv()
        print "result --- ", result
        result = json.loads(result)
        assert result['result'] == 'connected'
        assert result['id'] == 1

        r = requests.post('http://127.0.0.1:8888/device/UUID-12345/message', data={
            'switch_id': 1,
            'on_off': 1,
            'cmd': 'switch_light'
        })
        print ">>>", r.content
        assert 'OK' in r.content

        result = ws.recv()
        print "result --- ", result
        result = json.loads(result)
        assert result['cmd'] == 'switch_light'

        ws.close()

    def tearDown(self):
        self.process.terminate()

if __name__ == '__main__':
    unittest.main()