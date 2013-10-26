import os
import pickle
import re
from unidecode import unidecode

class NumberRegexMatching:
    def match(self, entry):
        return re.search("([0-9]+)\\s+(\\S+)", entry.fingerprint())

    def map(self, entry):
        """Return the simplified form, or None"""
        match = self.match(entry)
        if match != None:
            return match.group(2)
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

    def children(self):
        return self._children

    def Combined(title, entries):
        e = Entry({"title": title})
        e._children = entries
        return e


def mapPhase(entry):
    return [m.map(entry) for m in mappings]

def removeFingerprintsFrom(fingerprints, entries):
    return list(filter(lambda e: e.fingerprint() in fingerprints, entries))

def performMapping(entries):
    mapped = map(mapPhase, entries)
    #Collapse all entries that have the same non-None entries
    for i in range(len(mappings)):
        resultsForMapping = [m[i] for m in mapped]
        successes = list(filter(lambda x: x is not None, resultsForMapping))
        if len(successes) > 1:
            print("Combining %i entries" % len(successes))
            succcessEntries = [entries[index] if status != None else None for (index, status) in enumerate(resultsForMapping)]
            # resultsForMapping
            combinedEntry = mappings[i].reduce(succcessEntries)
            print("Combined into: " + combinedEntry.fingerprint())
            newEntries = removeFingerprintsFrom(successes, entries)
            newEntries.append(combinedEntry)
            return newEntries
    return entries


