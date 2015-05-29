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
import redis
import requests
import wss
import json
import os

os.environ['HIPOCHAT_REDIS_DB'] = "3"


class TestChat(unittest.TestCase):

    def setUp(self):
        self.redis_conn = redis.StrictRedis(db=3)
        self.redis_conn.flushdb()

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
        ws.close()

    def tearDown(self):
        self.process.terminate()

if __name__ == '__main__':
    unittest.main()