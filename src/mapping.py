import os
import re
from unidecode import unidecode


class Mapping:
    pass

class NumberRegexMatching:
    def match(self, entry):
        return re.search("([0-9]+)\\s+(\\S+)", entry.fingerprint())

    def map(self, entry):
        """Return the simplified form, or None"""
        match = self.match(entry)
        if match != None:
            m = Mapping()
            m.ident = match.group(2)
            m.value = entry
            return m
        return None

    def reduce(self, entries):
        """Combine multiple entries into a single entry"""
        matches = [self.match(entry) for entry in entries]
        values = [int(round(float(m.group(1)))) for m in matches]
        return Entry.Combined("%i %s" % (sum(values), matches[0].group(2)), entries)


mappings = [
    NumberRegexMatching()
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
            s = s.replace(word, str(value))
    return s

class Entry:
    def __init__(self, entry):
        self._entry = entry

    def title(self):
        return self._entry['title']

    def fingerprint(self):
        fingerprint = re.sub("\\W", " ", self.title())
        fingerprint = re.sub("\\s+", " ", fingerprint)
        fingerprint = unidecode(fingerprint)
        fingerprint = deHumanize(fingerprint)
        return fingerprint.strip()


def mapPhase(entry):
    return [m.map(Entry(entry)) for m in mappings]

def removeFingerprintsFrom(fingerprints, entries):
    return list(filter(lambda e: e.fingerprint() in fingerprints, entries))


def performMapping(entries):
    mapped = map(mapPhase, entries)
    #Collapse entries into dates, remove all None.
    perIdent = {}
    for l in mapped:
        for entry in l:
            if entry:
                if entry.ident not in perIdent:
                    perIdent[entry.ident] = []
                perIdent[entry.ident].append(entry)
    #Reduce last week into a single entry
    return perIdent


