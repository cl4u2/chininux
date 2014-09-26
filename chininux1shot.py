#!/usr/bin/env python2

import urllib2
from bs4 import BeautifulSoup
import sys
from ipaddress import *


GIURL = "http://wiki.ninux.org/GestioneIndirizzi"

query = sys.argv[1]

class row():
    def __init__(self, labels):
        self.labels = labels # keep 'em sorted
    def search(self, q):
        "search q in all field values and return a similarity ratio"
        try:
            address = ip_address(unicode(q))
        except:
            return 0.0
        r = 0.0
        for k, v in self.__dict__.iteritems():
            try:
                subnet = ip_network(unicode(v), strict=False)
            except ValueError:
                continue
            if address in subnet:
                r += 1.0
        return r
    def __repr__(self):
        r = ""
        for label in self.labels:
            r += "%s: %s\n" % (label, getattr(self, label))
        return r
    def __str__(self):
        return repr(self)

html_doc = urllib2.urlopen(GIURL)

soup = BeautifulSoup(html_doc)

rows = []
tables = soup.find_all('table')
for table in tables:
    labels = []
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if len(labels) == 0:
            labels = [next(td.strings).replace(' ', '_').replace('.', '_') for td in tds]
        else:
            r = row(labels)
            for i in range(len(tds)):
                try:
                    label = labels[i]
                except IndexError:
                    continue
                data = tds[i].get_text()
                setattr(r, label, data)
            rows.append(r)


for row in rows:
    if row.search(query) > 0.0:
        print row

