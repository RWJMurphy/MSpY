#!/usr/bin/env python
from __future__ import print_function

from datetime import datetime
import os
import re
import sys
import time
from urlparse import urlparse, parse_qs

from bs4 import BeautifulSoup
import requests

BASE_URL = "http://www.msy.com.au"
CATEGORY_URL = BASE_URL + "/default.jsp?category={cid:d}&page={page:d}"
PRODUCT_URL = BASE_URL + "/product.jsp?productId={pid:d}"
CATEGORIES = {
        "RAM": 28,
        "HDD": 12,
}

REGEXEN = {
    "HDD": {
        "capacity": (re.compile(r' ([0-9]+[MGT]B?)', re.I), str, 0),
        "speed": (re.compile(r' ([0-9]+)rpm', re.I), int, 1),
        "size": (re.compile(r' ([0-9.]+)"', re.I), float, 1),
        "ssd": (re.compile(r'\bssd\b', re.I), bool, 0),
        "sata": (re.compile(r' sata( ?[0-9]+| I+)?', re.I), str, 0),
    },
    "RAM": {
        "size": (re.compile(r'([0-9]+)GB?', re.I), int, 1),
        "ddr": (re.compile(r'ddr[23]?', re.I), str, 0),
        "clock": (re.compile(r'ddr[23]?[ -]?([0-9]+)', re.I), int, 1),
        "kit": (re.compile(r'\(([0-9]+GB?x[0-9]+)\)', re.I), str, 1),
    },
}

__all__ = ["MSpY"]


class MSpY(object):
    def __init__(self, request_delay=1):
        self.request_delay = request_delay
        self._last_get = datetime.min

    def _considerate_get(self, url):
        now = datetime.now()
        time_since_last = (now - self._last_get).total_seconds()
        time_until_next = self.request_delay - time_since_last
        if time_until_next >= 0:
            time.sleep(time_until_next)
        req = requests.get(url)
        self._last_get = datetime.now()
        return req

    def _parse_product_name(self, name, ptype):
        attributes = {}
        if ptype in REGEXEN:
            for a_name, (regex, a_type, group) in REGEXEN[ptype].iteritems():
                a_value = None
                matches = regex.search(name)
                if matches is not None:
                    a_value = a_type(matches.group(group))
                elif a_type == bool:
                    a_value = False
                attributes[a_name] = a_value
        return attributes

    def _extract_product(self, element):
        query_args = parse_qs(urlparse(element.find("a")['href']).query)
        pid = int(query_args['productId'][0])
        product = {
                "name": element.find(class_="title").get_text().strip(),
                "pid": int(pid),
                "price": float(element.find(class_="price").get_text().lstrip('$')),
        }
        return product

    def products(self, category=None, cid=None, ptype=None):
        if category is None:
            if cid is None or ptype is None:
                raise ValueError("You must supply category or cid and ptype")
        else:
            category = category.upper()
            if category in CATEGORIES:
                cid = CATEGORIES[category]
                ptype = category
            else:
                raise ValueError("Unknown category '{}'".format(category))

        for product in self._fetch_products_by_cid(cid, ptype):
            yield product

    def _fetch_products_by_cid(self, cid, ptype, page=1):
        req = self._considerate_get(CATEGORY_URL.format(cid=cid, page=page))
        soup = BeautifulSoup(req.text)
        product_elements = soup.find(class_="homeProGrid")("dd")
        for elem in product_elements:
            product = self._extract_product(elem)
            product.update(self._parse_product_name(product['name'], ptype))
            yield product

        next_page = page + 1
        if soup.find("a", href="?category={cid:d}&page={page:d}".format(cid=cid, page=next_page)):
            for product in self._fetch_products_by_cid(cid, ptype, next_page):
                yield product
        raise StopIteration
