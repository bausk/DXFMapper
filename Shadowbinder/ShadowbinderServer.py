# Created: 08.03.13
# License: MIT License
#from __future__ import unicode_literals
__author__ = "Alex Bausk <bauskas@gmail.com>"

import sys
from sys import argv
import collections
import time
import zmq
from zmq.eventloop import ioloop
ALIVE_URL = 'tcp://127.0.0.1:5556'

def init():
    return argv

def handler(alive_socket, *args, **kwargs):
    request = alive_socket.recv()
    reply = request.decode("utf_16")
    message = u"Received entity layer information: {}\n".format(reply)
    print(message.encode(sys.stdout.encoding))
    alive_socket.send(request)

def main():
    script, filename = init()

    print("Shadowbinder server starting...\n")
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(ALIVE_URL)

    io_loop = ioloop.IOLoop.instance()
    io_loop.add_handler(socket, handler, io_loop.READ)
    io_loop.start()
    
    #while True:
    #    server.recv()



if __name__ == '__main__':
    main()

