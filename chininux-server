#!/usr/bin/env python2
#
#  Copyright 2014 Claudio Pisa (clauz at ninux dot org)
#
#  This file is part of chininux
#
#  chininux is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  chininux is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with chininux.  If not, see <http://www.gnu.org/licenses/>.
#

from chininux import *
import threading
from SocketServer import BaseRequestHandler, ThreadingTCPServer
import time

class AddressRetriever(threading.Thread):
    def __init__(self, refreshInterval=300):
        self.alock = threading.Lock()
        self.adirs = [AddressDirectory(GIURLS), AddressDirectory(GIURLS)]
        self.currentadir = 0
        self.refreshInterval = refreshInterval
        self.ready = False
        threading.Thread.__init__(self)
    def run(self):
        while True:
            nextcurrentadir = (self.currentadir + 1) % 2
            self.adirs[nextcurrentadir].refresh()
            print "fresh!"
            self.alock.acquire()
            self.currentadir = nextcurrentadir
            self.ready = True
            self.alock.release()
            time.sleep(self.refreshInterval)
    def search(self, query):
        self.alock.acquire()
        if self.ready:
            r = self.adirs[self.currentadir].search(query)
        else:
            r = ["Sorry, the whois server is not ready yet :(\n"]
        self.alock.release()
        return r

class WhoisRequestHandler(BaseRequestHandler):
    def handle(self):
        query = self.request.recv(4096)
        response = "\n".join([str(r) for r in self.server.ar.search(query)])
        self.request.sendall(response)

class WhoisServer(ThreadingTCPServer):
    def __init__(self):
        self.ar = AddressRetriever()
        self.ar.start()
        ThreadingTCPServer.__init__(self, ("0.0.0.0", 43), WhoisRequestHandler)

if __name__ == "__main__":
    whoisServer = WhoisServer()
    whoisServer.serve_forever()


