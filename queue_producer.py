from redis import Redis
from rq import Queue
import json
from consumer import process_webhook

# Super-simple async processing setup
class QueueProducer(object):
    def __init__(self, redis_host="localhost", redis_port=6379):
        self.redis_host = redis_host
        self.redis_port = redis_host

        self.redis_connection = Redis(host=redis_host, port=redis_port)
        self.queue = Queue(connection=self.redis_connection)

    def enqueue(self, message: str):
        self.queue.enqueue(process_webhook, json.loads(message))
