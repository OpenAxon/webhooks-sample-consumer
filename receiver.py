from flask import Flask
from flask import request
from flask import Response
from queue_producer import QueueProducer
from credentials import WEBHOOK_HMAC_SECRET
import hmac
import hashlib

# This is the endpoint designed to receive webhooks.
# Run this with:
# flask --app receiver run --port 8080


QUEUE_PRODUCER = QueueProducer()

app = Flask(__name__)

# Derives the HMAC signature from the incoming webhook payload and
# checks that it matches the provided signature
def authenticate(body: bytes, sig: str):
    derived_hmac_sig = hmac.new(WEBHOOK_HMAC_SECRET, body, hashlib.sha256).hexdigest()
    return derived_hmac_sig == sig


@app.route("/api/v1/webhooks/cases", methods=["POST"])
def receive_webhook():
    if request.method != "POST":
        return Response(response='{"error": "All requests must be POSTs"}', status=400)
    hmac_sig = request.headers.get("x-axon-body-hmac")
    is_authenticated = authenticate(body=request.data, sig=hmac_sig)
    if not is_authenticated:
        return Response(response='{"error": "unauthorized"}', status=401)
    # If the body is empty, this is an endpoint-validation request. Do nothing
    if request.data == "{}".encode("utf-8"):
        return Response(response="", status=200)
    # Enqueue the request for processing
    else:
        QUEUE_PRODUCER.enqueue(message=request.data.decode("utf-8"))
    return Response(response="", status=200)
