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

class Row():
    def __cleanlabel(self, label):
        return label.replace(' ', '_').replace('.', '_').replace('/', '_').strip()
    def __init__(self, section, labels):
        self.section = section # the name of the page section
        self.labels = [self.__cleanlabel(l) for l in labels] # to preserve the order of the table columns
    def __setattr__(self, name, value):
        n = self.__cleanlabel(name)
        if '-' in value:
            self.__dict__[n] = value
            i = 0
            for v in value.split('-'):
                n = "%s_%s" % (n, i)
                setattr(self, n, v)
                i+=1
        else:
            try:
                v = value.strip()
                subnet = ip_network(unicode(v), strict=False)
                self.__dict__[n] = subnet
            except ValueError,e :
                #print "bad network: %s [%s]" % (v, e)
                self.__dict__[n] = value
            except:
                self.__dict__[n] = value
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
            if not type(v) is IPv4Network and not type(v) is IPv6Network:
                continue
            # v is a network
            if address in v:
                r += 1.0 * v.prefixlen / v.max_prefixlen
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
        "return a list of Row objects from a table"
        rrows = []
        labels = []
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(labels) == 0:
                labels = [td.get_text() for td in tds]
            else:
                r = Row(currentsection, labels)
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
        "fetch an URL content and return a list of corresponding Row objects"
        html_doc = urllib2.urlopen(url)
        soup = BeautifulSoup(html_doc)
        pagetitle = soup.find("title")
        currentsection = ""
        for t in soup.find_all("table"):
            titles = [pagetitle] + [t.find_previous(tag) for tag in ["h1", "h2", "h3"]]
            currentsection = "\n".join([title.get_text() for title in titles if title != None])
            self.rows.extend(self.__processtable(t, currentsection))
    def refresh(self):
        for url in self.urls:
            self.retrieveandparse(url)
    def search(self, query):
        "return all the rows that match a query"
        res = []
        for row in self.rows:
            if row.search(query) > 0.0:
                res.append(row)
        return res


