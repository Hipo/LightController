import os
import json
import pika

from _collections import defaultdict
import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado import gen
from pika.adapters.tornado_connection import TornadoConnection
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import logging
import datetime
import calendar

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


RABBIT_URL = os.getenv('RABBIT_URL', None)
RABBIT_USERNAME = os.getenv('RABBIT_USERNAME', 'guest')
RABBIT_PASS = os.getenv('RABBIT_PASS', 'guest')

PORT = os.getenv('LISTEN_PORT', 8888)
ADDRESS = os.getenv('LISTEN_ADDRESS', '0.0.0.0')


pika_connected = False
websockets = defaultdict(set)

class PikaClient(object):

    def __init__(self, io_loop):
        self.connected = False
        self.connecting = False
        self.connection = None
        self.channel = None
        self.ioloop = io_loop

    def connect(self):

        if self.connecting:
                logger.info('PikaClient: Already connecting to RabbitMQ')
                return

        logger.info('PikaClient: Connecting to RabbitMQ on port 5672, Object: %s', self)

        self.connecting = True

        credentials = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASS)
        param = pika.ConnectionParameters(host=RABBIT_URL,
                                          port=5672,
                                          virtual_host="/",
                                          credentials=credentials)
        self.connection = TornadoConnection(param,
                                            on_open_callback=self.on_connected)

        global pika_connected
        pika_connected = True

    def on_connected(self, connection):
        logger.info('PikaClient: Connected to RabbitMQ on :5672')
        self.connected = True
        self.connection = connection
        self.connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        logger.info('PikaClient: Channel Open, Declaring Exchange, Channel ID: %s', channel)
        self.channel = channel

        self.channel.exchange_declare(exchange='tornado',
                                      type="direct",
                                      durable=False,
                                      auto_delete=True)

    def declare_queue(self, token):
        logger.info('PikaClient: Exchange Declared, Declaring Queue')
        self.queue_name = token
        self.channel.queue_declare(queue=self.queue_name,
                                   durable=False,
                                   auto_delete=True,
                                   callback=self.on_queue_declared)

    def on_queue_declared(self, frame):
        self.channel.queue_bind(exchange='tornado',
                                queue=self.queue_name,
                                routing_key=self.queue_name,
                                callback=self.on_queue_bound)

    def on_queue_bound(self, frame):
        logger.info('PikaClient: Queue Bound, Issuing Basic Consume')
        self.channel.basic_consume(consumer_callback=self.on_pika_message,
                                   queue=self.queue_name,
                                   no_ack=True)

    def on_pika_message(self, channel, method, header, body):
        logger.info('PikaCient: Message receive, delivery tag #%i', method.delivery_tag)
        message = json.loads(body)
        for i in websockets[message['token']]:
            try:
                i.write_message(body)
            except:
                logger.exception("exception while writing message to client")

    def on_basic_cancel(self, frame):
        logger.info('PikaClient: Basic Cancel Ok')
        # If we don't have any more consumer processes running close
        self.connection.close()

    def on_closed(self, connection):
        # We've closed our pika connection so stop the demo
        self.ioloop.IOLoop.instance().stop()

    def sample_message(self, ws_msg):
        token = json.loads(ws_msg)['token']
        properties = pika.BasicProperties(
            content_type="text/plain", delivery_mode=1)
        self.channel.basic_publish(exchange='tornado',
                                   routing_key=token,
                                   body=ws_msg,
                                   properties=properties)


from tornado.web import HTTPError

def assert_(condition, status=400, message=None):
    if not condition:
        raise HTTPError(status, log_message=message)

class BaseHandler(tornado.web.RequestHandler):
    pass

class IndexHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        self.write("hello")
        self.finish()


def get_utc_timestamp():
    ts = calendar.timegm(datetime.datetime.utcnow().timetuple())
    return ts


class WebSocketDeviceHandler(tornado.websocket.WebSocketHandler):
    chat_token = None
    profile = None

    def check_origin(self, origin):
        return True

    @gen.coroutine
    def assert_(self, condition, message):
        if not condition:
            self.clear()
            self.write_message(json.dumps(dict({"ERROR": message})))
            self.close()

    @gen.coroutine
    def open(self, *args, **kwargs):
        logger.info('new connection')

        self.device_uuid = args[0]
        pika_client.declare_queue(self.device_uuid)
        pika_client.websocket = self
        websockets[self.device_uuid].add(self)

    def cmd_hello(self, data):
        return 'connected'

    def cmd_dummy(self, data):
        return 'pong'

    def cmd_register(self, data):
        return 'ok'

    def dispatch_message(self, message):
        cmd = message.get('cmd', 'dummy')

        fn = getattr(self, 'cmd_%s' % cmd, None)
        if fn:
            reply = fn(message)
            pika_client.sample_message(json.dumps({
                'result': reply,
                'token' : self.device_uuid,
                'id': message['id']
            }))

    def on_message(self, message):
        ts = get_utc_timestamp()
        message_dict = json.loads(message)
        message_dict.update({'timestamp': ts})
        message_dict.update({'token': self.device_uuid})
        # dont echo back
        # pika_client.sample_message(json.dumps(message_dict))
        try:
            self.dispatch_message(message_dict)
        except:
            logger.exception("exception")

    def send_msg(self, msg):
        ts = get_utc_timestamp()
        msg.update({'timestamp': ts})
        msg.update({'token': self.device_uuid})
        pika_client.sample_message(json.dumps(msg))


    def on_close(self):
        logger.info("closing connection")
        websockets[self.chat_token].discard(self)
        ts = get_utc_timestamp()


class MessageToDeviceHandler(BaseHandler):

    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        self.write("unsupported")
        self.finish()

    @tornado.web.asynchronous
    def post(self, device_id):
        cmd = self.get_argument('cmd', None)
        switch_id = self.get_argument('switch', None)
        on_off = self.get_argument('switch', None)

        clients = websockets[device_id]
        for client in clients:
            client.send_msg({'cmd': cmd, 'id': int(time.time()),'switch_id': switch_id, 'on_off': on_off})

        self.write("OK")
        self.finish()

import time

app = tornado.web.Application([(r'/wss/device/([a-zA-Z\-0-9\.:,_-]+)/?', WebSocketDeviceHandler),
                               (r'/device/([a-zA-Z\-0-9\.:,_-]+)/message?', MessageToDeviceHandler),
                               (r'/index/?', IndexHandler)])

pika_client = None

def ping_all():
    for k, v in websockets.iteritems():
        print k, v
        for s in v:
            s.send_msg({'cmd': 'ping', 'id': 123})

def run():
    global pika_client
    logger.info("Listening to %s:%s", ADDRESS, PORT)
    app.listen(PORT, ADDRESS)
    ioloop = tornado.ioloop.IOLoop.instance()
    pika_client = PikaClient(ioloop)
    pika_client.connect()

    task = tornado.ioloop.PeriodicCallback(
            ping_all,
            10000)
    task.start()


    ioloop.start()

if __name__ == '__main__':
    run()