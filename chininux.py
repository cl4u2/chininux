#!/usr/bin/env python2

import urllib2
from bs4 import BeautifulSoup
import sys
from ipaddress import *

GIURLS = ["http://wiki.ninux.org/GestioneIndirizzi",
          "http://wiki.ninux.org/IndirizziCalabria",
          "http://wiki.ninux.org/Firenze/GestioneIndirizzi",
          "http://wiki.ninux.org/IndirizziMarche",
          "http://wiki.ninux.org/indirizzi-sicilia"
         ]

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

class AddressDirectory():
    def __init__(self, urls):
        "urls: list of URLs to fetch addresses from"
        self.urls = urls
        self.rows = []
    def __processtable(self, table, currentsection=""):
        "return a list of row objects from a table"
        rrows = []
        labels = []
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(labels) == 0:
                labels = [td.get_text().replace(' ', '_').replace('.', '_') for td in tds]
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
    def retrieveandparse(self, url):
        "fetch an URL content and return a list of corresponding row objects"
        html_doc = urllib2.urlopen(url)
        soup = BeautifulSoup(html_doc)
        currentsection = ""
        for t in soup.find_all("table"):
            titles = [t.find_previous(tag) for tag in ["h1", "h2", "h3"]]
            currentsection = "\n".join([title.get_text() for title in titles if title != None])
            self.rows.extend(self.__processtable(t, currentsection))
    def start(self):
        for url in self.urls:
            self.retrieveandparse(url)
    def search(self, query):
        "return all the rows that match a query"
        res = []
        for row in self.rows:
            if row.search(query) > 0.0:
                res.append(row)
        return res


