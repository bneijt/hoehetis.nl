import os
import re
from unidecode import unidecode
import datetime
import time

class MappedEntry:
    def __init__(self, entry, ident, count):
        assert type(count) == type(1)
        self._count = count
        self._ident = ident
        self._entry = entry
    def ident(self):
        return self._ident
    def count(self):
        return self._count
    def published(self):
        #print(type(self._entry["published_parsed"]))
        return  datetime.datetime.fromtimestamp(time.mktime(self._entry["published_parsed"]))
    def entry(self):
        return self._entry

class NumberRegexMatchingMapping:
    def match(self, entry):
        return re.search("([0-9]+)\\s+(\\S+)", fingerprint(entry))

    def map(self, entry):
        """Return the simplified form, or None"""
        match = self.match(entry)
        if match != None:
            return MappedEntry(
                entry,
                match.group(2).lower(),
                int(round(float(match.group(1))))
            )
        return None

class IdMapping:
    def map(self, entry):
        """Return the simplified form, or None"""
        return MappedEntry(entry, "berichten", 1)


mappings = [
    NumberRegexMatchingMapping(),
    IdMapping()
]

def deHumanize(s):
    mapping = {
        "een": 1,
        "één": 1,
        "twee": 2,
        "drie": 3,
        "vier": 4,
        "vijf": 5,
        "zes": 6,
        "zeven": 7,
        "acht": 8,
        "negen": 9,
        "tien": 10,
        "veertig": 40,
        "duizend": 1000
    }
    for (word, value) in mapping.items():
        if word in s:
            s = s.replace(" %s " % word, str(value))
    return s

def fingerprint(entry):
    fingerprint = re.sub("\\W", " ", " %s " % entry["title"])
    fingerprint = re.sub("\\s+", " ", fingerprint)
    fingerprint = unidecode(fingerprint)
    fingerprint = deHumanize(fingerprint)
    return fingerprint.strip()


def mapPhase(entry):
    return [m.map(entry) for m in mappings]



def performMapping(entries):
    listsOfMapped = map(mapPhase, entries)
    mapping = []
    for m in listsOfMapped:
        mapping.extend(m)
    while None in mapping:
        mapping.remove(None)
    return mapping


