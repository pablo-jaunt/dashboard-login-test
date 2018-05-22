#!/usr/bin/env python3
# Import your application as:
# from app import application
# Example:

from app import app
import json

# Import CherryPy
import cherrypy

CONFIG = {}

try:
    with open('settings/config.json') as config_file:
        CONFIG = json.load(config_file)
except IOError:
    print("No configuration found.  Exiting.")
    raise

if __name__ == '__main__':

    # Mount the application
    cherrypy.tree.graft(app, "/")

    # Unsubscribe the default server
    cherrypy.server.unsubscribe()

    # Instantiate a new server object
    server = cherrypy._cpserver.Server()

    # Configure the server object
    server.socket_host = "0.0.0.0"
    server.socket_port = 8443
    server.thread_pool = 30

    # For SSL Support
    server.ssl_module = 'builtin'
    server.ssl_certificate = CONFIG.get('tls_cert_file', 'cert/tls.crt')
    server.ssl_private_key = CONFIG.get('tls_key_file', '/cert/tls.key')
    # server.ssl_certificate_chain = 'ssl/bundle.crt'

    # Subscribe this server
    server.subscribe()

    # Start the server engine (Option 1 *and* 2)
    cherrypy.engine.start()
    cherrypy.engine.block()
