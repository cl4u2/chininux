#!/usr/bin/env python2

import urllib2
from bs4 import BeautifulSoup
import sys
from ipaddress import *


GIURL = "http://wiki.ninux.org/GestioneIndirizzi"

query = sys.argv[1]

class row():
    def __init__(self, section, labels):
        self.section = section # the name of the page section
        self.labels = labels # keep 'em sorted
    def search(self, q):
        "search q in all field values and return a similarity ratio"
        try:
            address = ip_address(unicode(q.strip()))
        except:
            return 0.0
        r = 0.0
        for k, v in self.__dict__.iteritems():
            if k in ["section", "labels"]:
                continue
            try:
                subnet = ip_network(unicode(v.strip()), strict=False)
            except ValueError,e :
                #print "bad network: %s [%s]" % (v, e)
                continue
            except AttributeError:
                continue
            if address in subnet:
                r += 1.0
        return r
    def __repr__(self):
        r = ""
        if len(self.section) > 0:
            r += "  "
            r += self.section.replace("\n", "\n  ")
            r += "\n\n"
        for label in self.labels:
            r += "%s: %s\n" % (label, getattr(self, label))
        return r
    def __str__(self):
        return repr(self)

def processtable(table, currentsection=""):
    "return a list of row objects from a table"
    rrows = []
    labels = []
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if len(labels) == 0:
            labels = [next(td.strings).replace(' ', '_').replace('.', '_') for td in tds]
        else:
            r = row(currentsection, labels)
            for i in range(len(tds)):
                try:
                    label = labels[i]
                except IndexError:
                    continue
                data = tds[i].get_text()
                setattr(r, label, data)
            rrows.append(r)
    return rrows

html_doc = urllib2.urlopen(GIURL)
soup = BeautifulSoup(html_doc)

rows = []
currentsection = ""
for t in soup.find_all("table"):
    currentsection = "\n".join([t.find_previous(tag).get_text() for tag in ["h1", "h2", "h3"]])
    rows.extend(processtable(t, currentsection))

for row in rows:
    if row.search(query) > 0.0:
        print row

