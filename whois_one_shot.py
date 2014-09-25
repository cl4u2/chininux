#!/usr/bin/env python2

import urllib2
from bs4 import BeautifulSoup
import Levenshtein
import sys


GIURL = "http://wiki.ninux.org/GestioneIndirizzi"

query = sys.argv[1]

class row():
    def __init__(self, labels):
        self.labels = labels # keep 'em sorted
    def search(self, q):
        "search q in all field values and return a similarity ratio"
        maxsim = 0.0
        for k, v in self.__dict__.iteritems():
            r = Levenshtein.ratio(unicode(q), unicode(v))
            maxsim = max(r, maxsim)
        return maxsim
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
        #print tds
        if len(labels) == 0:
            labels = [next(td.strings).replace(' ', '_').replace('.', '_') for td in tds]
            #print labels
        else:
            r = row(labels)
            for i in range(len(tds)):
                try:
                    label = labels[i]
                except IndexError:
                    continue
                try:
                    data = next(tds[i].strings)
                except StopIteration:
                    continue
                setattr(r, label, data)
            #print r
            rows.append(r)


bestrow = None
bestvalue = 0.0
for row in rows:
    v = row.search(query)
    if v > bestvalue:
        bestrow = row
        bestvalue = v

print bestrow

