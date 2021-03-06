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
from netaddr import EUI
from phpipam.phpipam import PHPIPAM
import settings
import json

class Record():
    "an (IP address) record"
    def __cleanlabel(self, label):
        "remove some special characters from the label name"
        return label.replace(' ', '_').replace('.', '_').replace('/', '_').replace('&','_').strip()
    def __cleanhost(self, host):
        "remove special characters from the host name"
        r = []
        for c in host:
            if ord(c) in range(ord('a'), ord('z')+1) + range(ord('A'), ord('Z')+1) + range(ord('0'), ord('9')+1):
                    r.append(c)
            else:
                    r.append('_')
        return "".join(r)

    def __init__(self, section, labels):
        # the labels will be the only properties that will be printed out in the __repr__ function
        self.section = section # the name of the page section
        self.labels = [self.__cleanlabel(l) for l in labels] # to preserve the order of the table columns
    def __setattr__(self, name, value):
        n = self.__cleanlabel(name)
        # we need this because some cells may contain two addresses separated by a dash
        if '-' in value:
            value = value.replace("-", " ")
        if ' ' in value:
            self.__dict__[n] = value
            i = 0
            for v in value.split(' '):
                if len(v) == 0:
                    continue
                n = "%s_%s" % (n, i)
                setattr(self, n, v)
                i+=1
        else:
            try:
                v = value.strip()
                mac = EUI(unicode(v), version=48)
                self.__dict__[n] = mac
                return
            except:
                pass
            try:
                v = value.strip()
                if not '/' in v:
                    ipa = ip_address(unicode(v))
                    if type(ipa) is IPv4Address:
                        v += "/32"
                    elif type(ipa) is IPv6Address:
                        v += "/128"
                subnet = ip_network(unicode(v), strict=False)
                self.__dict__[n] = subnet
            except ValueError,e :
                #print "bad network: %s [%s]" % (v, e)
                self.__dict__[n] = value
            except:
                self.__dict__[n] = value
    def search(self, q):
        "search q in all field values and return a similarity ratio between 0 and 1"
        try:
            address = ip_address(unicode(q.strip()))
        except:
            try:
                address = EUI(unicode(q.strip()))
            except:
                return 0.0
        r = 0.0
        for k, v in self.__dict__.iteritems():
            if k in ["section", "labels"]:
                continue
            if type(address) is EUI:
                if type(v) is EUI:
                    if v == address:
                        r += 1.0
            else:
                assert type(address) is IPv4Address or type(address) is IPv6Address
                if not type(v) is IPv4Network and not type(v) is IPv6Network:
                    continue
                # v is a network
                if address in v:
                    r += 1.0 * v.prefixlen / v.max_prefixlen
        return r
    def hosts(self):
        "return the host stored in this object or None"
        hostname = ""
        hostaddr = ""
        node = ""
        device = ""
        for k, v in self.__dict__.iteritems():
            if k == "node":
                node = self.__cleanhost(v)
            if k == "device":
                device = self.__cleanhost(v)
            if type(v) is IPv4Network:
                if v.prefixlen == 32:
                    hostaddr = str(v.network_address)
            elif type(v) is IPv6Network:
                if v.prefixlen == 128:
                    hostaddr = str(v.network_address)
        hostname = ".".join([node, device])
        if len(hostname) < 2 or len(hostaddr) == 0:
            return None
        return (hostaddr, hostname)

    def __repr__(self):
        "return a RIPE-whois-like representation"
        r = ""
        if len(self.section) > 0:
            r += "% "
            r += self.section.replace("\n", "\n% ")
            r += "\n\n"
        for label in self.labels:
            goodlabel = label.strip('_').lower()
            goodlabel = goodlabel.replace('_', '-')
            goodlabel = '-'.join([word for word in goodlabel.split('-') if len(word) > 0])
            goodlabel += ":"
            goodvalue = str(getattr(self, label)).strip()
            if len(goodvalue) == 0:
                goodvalue = "-"
            r += "{0:20} {1}\n".format(goodlabel, goodvalue)
        return r
    def __str__(self):
        return repr(self)

class AddressDirectory():
    def __init__(self, urls):
        "urls: list of URLs to fetch addresses from"
        self.urls = urls
        self.records = []
    def __processtable(self, table, currentsection=""):
        "return a list of Record objects from an HTML table"
        rrecords = []
        labels = []
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(labels) == 0:
                labels = [td.get_text() for td in tds]
            else:
                r = Record(currentsection, labels)
                for i in range(len(tds)):
                    try:
                        label = labels[i]
                    except IndexError:
                        continue
                    data = tds[i].get_text()
                    setattr(r, label, data)
                rrecords.append(r)
        return rrecords
    def __process_phpipam(self, server, api_id, api_key):
        rrecords = []
        ipam = PHPIPAM(server, api_id, api_key)
        jsubnets = ipam.read_subnets()
        subnets = json.loads(jsubnets)
        for s in subnets['data']:
            labels = ['subnet', 'description']
            r = Record("phpipam: " + server, labels)
            for label in labels:
                setattr(r, label, unicode(s[label]))
            #subnet override
            setattr(r, "subnet", "%s/%s" % (unicode(s['subnet']), unicode(s['mask'])))
            rrecords.append(r)
        return rrecords
    def __process_nodeshot_api(self, url):
        rrecords = []
        httpurl = "http" + url[8:] + "/api/v1/whois/?format=json"
        nsapi = urllib2.urlopen(httpurl)
        jaddresses = " ".join(nsapi.readlines())
        addresses = json.loads(jaddresses)
        for a in addresses:
            labels = a.keys()
            r = Record("nodeshot: " + url, labels)
            for label in labels:
               setattr(r, label, unicode(a[label]))
            rrecords.append(r)
        return rrecords
    def retrieveandparse(self, url):
        "fetch an URL content and populate a list of corresponding Record objects"
        if url.startswith("phpipam://"):
            # fetch phpIPAM records
            try:
                api_id, api_key = url[10:].split("@")[0].split(":")
                server = url.split("@")[1]
            except Exception, e:
                print "%s: Invalid or missing api id and api key [%s]" % (url, e)
                return
            self.records.extend(self.__process_phpipam(server, api_id, api_key))
            return
        elif url.startswith("nodeshot://") or url.startswith("nodeshots://"):
            # transform the nodeshot:// or nodeshots:// URL into http:// or https://
            self.records.extend(self.__process_nodeshot_api(url))
            return
        elif url.startswith("http://") or url.startswith("https://"):
            html_doc = urllib2.urlopen(url)
        elif url.startswith("file://"):
            filename = url[7:]
            html_doc = open(filename)
        else:
            return
        # take an HTML document, either local (file://) or retrieved from the Web (http://, https://)
        # and parse all the HTML tables contained in it
        soup = BeautifulSoup(html_doc, "lxml")
        pagetitle = soup.find("title").get_text()
        currentsection = ""
        for t in soup.find_all("table"):
            titles = [t.find_previous(tag) for tag in ["h1", "h2", "h3"]]
            currentsection = "\n".join([pagetitle, url] + [title.get_text() for title in titles if title != None])
            self.records.extend(self.__processtable(t, currentsection))
    def refresh(self):
        self.records = []
        for url in self.urls:
            try:
                self.retrieveandparse(url)
            except Exception, e:
                print "could not retrieve url %s: %s" % (url, e)
                continue
    def search(self, query):
        "return all the records that match a query, and sort them by increasing similarity ratio"
        queryresults = [(record.search(query), record) for record in self.records]
        queryresults = [(ratio, record) for (ratio, record) in queryresults if ratio > 0.0]
        queryresults.sort(key=lambda tup: tup[0])
        results = [record for (ratio, record) in queryresults]
        if len(results) == 0:
            results = ["%% Sorry, no record matched your query: %s\n" % query]
            return results
        return [settings.headerstring] + results + [settings.footerstring]

    def hosts(self):
        return [record.hosts() for record in self.records if record.hosts() != None]


