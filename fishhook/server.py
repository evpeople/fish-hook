import hmac
import json as js
import os

from sanic import Sanic
from sanic.response import json
from hashlib import sha1
from .settings import REQUIRED_HEADERS
from .fishhook import FishHook
from http.server import HTTPServer, BaseHTTPRequestHandler

from .utils import find_main_directory

server = Sanic(name='hook')

@server.post('/<name>')
async def serve(request, name):
    headers = request.headers
    body = request.body
    secret = FishHook.get_secret(name)
    base_path = find_main_directory(os.getcwd())
    app_path = os.path.join(base_path, name)
    json_file_path = os.path.join(app_path,'message.json')

    file=open(json_file_path,'w+')
    file.write(body.decode())

    file.close()
    if secret == None:
        return json({'message': "No register app!"}, status=400)

    # If set the secret, SHA1 encryption.
    signature =  'sha1=' + sign(secret.encode(encoding='utf-8'), body) if secret != "" else None

    # Check headers
    if loss_header(headers):
        return json({"message": "Lack of some special fields in request header!"}, status=400)

    # Check signature, if secret exists
    correct_signature = headers.get('x-hub-signature', None)

    if signature != correct_signature:
      return json({'message': "The secret is mismatching!"}, status=400)

    # Get the event from Github
    event = headers['x-github-event']

    # If event is `ping`, ignore it
    # Else, distributing the event
    if event != 'ping':
        FishHook.execute_event(name, event)

    return json({'message': 'ok!'})

def loss_header(headers):
    # Get union set
    return 0

def sign(secret, body):
    hashed = hmac.new(secret, body, sha1)
    return hashed.hexdigest()

def errorHandler(msg):
    return json({'message': msg})
