import os
import pickle
import re


class NumberRegexMatching:
    def map(self, entry):
        """Return the simplified form, or None"""
        match = re.search("([0-9]+)\\s+(\\S+)", entry.fingerprint())
        if match != None:
            return match.group(2)
        return None

    def reduce(self, entries):
        """Combine multiple entries into a single entry"""
        return entries[0]


mappings = [
    NumberRegexMatching()
]


class Entry:
    def __init__(self, entry):
        self.entry = entry
    def title(self):
        return self.entry['title']
    def fingerprint(self):
        fingerprint = re.sub("\\s+", " ", self.title())
        return fingerprint.strip()


def mapPhase(entry):
    return [m.map(entry) for m in mappings]

def removeFingerprintsFrom(fingerprints, entries):
    return list(filter(lambda x: x.fingerprint() not in fingerprints, entries))

def performMapping(entries):
    mapped = map(mapPhase, entries)
    #Collapse all entries that have the same non-None entries
    for i in range(len(mappings)):
        resultsForMapping = [m[i] for m in mapped]
        successes = list(filter(lambda x: x is not None, resultsForMapping))
        if len(successes) > 1:
            print("Combining %i entries" % len(successes))
            combinedEntry = mappings[i].reduce(successes)
            newEntries = removeFingerprintsFrom(successes, entries)
            newEntries.append(combinedEntry)
            return newEntries
    return entries


