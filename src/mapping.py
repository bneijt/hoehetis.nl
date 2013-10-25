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

def deHumanize(s):
    mapping = {"veertig": 40}
    for (word, value) in mapping.items():
        if word in s:
            s = s.replace(word, str(value))
    return s
class Entry:
    def __init__(self, entry):
        self.entry = entry
    def title(self):
        return self.entry['title']
    def fingerprint(self):
        fingerprint = re.sub("\\W", " ", self.title())
        fingerprint = re.sub("\\s+", " ", fingerprint)
        fingerprint = deHumanize(fingerprint)
        return fingerprint.strip()


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


