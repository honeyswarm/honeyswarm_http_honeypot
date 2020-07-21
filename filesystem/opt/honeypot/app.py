#!/usr/bin/python3.8
import os
import json
import random
import asyncio
from asyncio import wait_for

from aiohttp import web
from hpfeeds.asyncio import ClientSession

SERVER_VERSIONS = [
    "Apache/2.4.18 (Ubuntu)",
    "Apache/2.4.20",
    "Apache/2.4.2",
    "Apache/2.4.6",
    "ATS/8.0.7"
    "Apache",
    "nginx",
    "nginx/1.14.0 (Ubuntu)",
    "nginx/1.18.0",
    "nginx/1.17.4",
    "nginx/1.15.7"
]

HPFSERVER = os.environ.get("HPFSERVER", "127.0.0.1")
HPFPORT = int(os.environ.get("HPFPORT", 20000))
HPFIDENT = os.environ.get("HPFIDENT", "testing")
HPFSECRET = os.environ.get("HPFSECRET", "secretkey")
HIVEID = os.environ.get("HIVEID", "UnknownHive")

def html_response(text):
    return web.Response(text=text, content_type='text/html')

def json_response(text):
    return web.Response(text=text, content_type='application/json')

async def on_prepare(request, response):
    """Sets the Reponse Server string to user selected or random choice or known version"""
    server_string = os.environ.get("SERVER_STRING", random.choice(SERVER_VERSIONS))
    if server_string == "random":
        server_string = random.choice(SERVER_VERSIONS)
    response.headers['Server'] = server_string

async def hpfeeds_publish(event_message):
    async with ClientSession(HPFSERVER, HPFPORT, HPFIDENT, HPFSECRET) as client:
        client.publish('http.sessions', json.dumps(event_message).encode('utf-8'))
    return True


async def handle(request):

    # ToDo, modify the response based on what has been requested. 
    # Or server a random HTML page
    name = request.match_info.get('name', "Anonymous")

    # For Now jsut going to always return a 200 with an HTML page. 
    text = """<html>
    <head></head>
    <body>
    <p>Under Maintainance</p>
    </body>
    </html>
    """

    print("{0} request for {1}".format(request.method, request.path))

    # Get HTTP as version string
    http_version = "HTTP/{0}.{1}".format(request.version.major, request.version.minor)

    # convert Cookies to a standard dict, We will loose Duplicates
    http_cookies = {}
    for k, v in request.cookies.items():
        http_cookies[k] = v

    # convert Headers to a standard dict, We will loose Duplicates
    http_headers = {}
    for k, v in request.headers.items():
        http_headers[k] = v

    # convert POST to a standard dict, We will loose Duplicates
    http_post = {}
    if request.method == 'POST':
        data = await request.post()
        for key, value in data.items():
            http_post[key] = value

    event_message = {
        "hive_id": HIVEID,
        "src_ip": request.remote,
        "http_remote": request.remote,
        "http_host": request.host,
        "http_version": http_version,
        "http_method": request.method,
        "http_scheme": request.scheme,
        "http_query": request.path_qs,
        "http_post": http_post,
        "http_headers": http_headers,
        "http_path": request.path
    }

    # Send the Broker message
    # Set timeout to 3 seconds in a try: except so we dont kill the http response
    try:
        await wait_for(hpfeeds_publish(event_message), timeout=3)
    except asyncio.TimeoutError:
        print("Unable to connect to hpfeeds broker.")
        pass

    # Send the response to the client
    return html_response(text)

app = web.Application()
app.on_response_prepare.append(on_prepare)
app.router.add_route('*', '/{name:.*}', handle)
#web.run_app(app, port=8181)

