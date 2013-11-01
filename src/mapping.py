# -*- coding: utf-8 -*-
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
        return  datetime.datetime.fromtimestamp(time.mktime(self._entry["published_parsed"]))
    def entry(self):
        return self._entry

class DeathTollMapping:
    deadWords = ["zelfmoord"]
    def simple(self, entry):
        fingerprint = entry["title"]
        fingerprint = " %s " % fingerprint
        fingerprint = re.sub("([0-9]+)\.([0-9]+)", "\\1\\2", fingerprint)
        # fingerprint = re.sub("\\W", " ", fingerprint)
        fingerprint = re.sub("\\s+", " ", fingerprint)
        fingerprint = unidecode(fingerprint)
        fingerprint = deHumanize(fingerprint)
        return " %s " % fingerprint.strip()

    def map(self, entry):
        """Return the simplified form, or None"""
        fingerprint = self.simple(entry)
        match = re.search("([0-9]+)\\s+([a-z]+\\s)?(doden|overledenen|gestorven|omgekomen)", fingerprint)
        if match != None:
            return MappedEntry(
                entry,
                "doden",
                int(round(float(match.group(1))))
            )
        match = re.search("([0-9]+)\\s+dode\\s+[a-zA-Z]+", fingerprint)
        if match != None:
            return MappedEntry(
                entry,
                "doden",
                int(round(float(match.group(1))))
            )
        for dw in self.deadWords:
            if dw in fingerprint:
                return MappedEntry(entry, "doden", 1)
        return None


class IncDecMapping:
    incWords = ["neemt toe", "vaker", "winnen terrein", "stijgt", "verbeteren kwaliteit"]
    incRegex = ["meer [a-z]+"]
    decWords = ["neemt af", "minder vaak", "verliezen terrein", "daalt", "verslechten kwaliteit"]
    decRegex = ["minder [a-z]+"]

    def map(self, entry):
        t = " %s " % entry["title"].lower()
        for ir in self.incRegex:
            if re.search(" %s " % ir, t):
                return MappedEntry(entry, "neemt toe", 1)
        for iw in self.incWords:
            if (" %s " % iw) in t:
                return MappedEntry(entry, "neemt toe", 1)
        for dr in self.decRegex:
            if re.search(" %s " % dr, t):
                return MappedEntry(entry, "neemt af", 1)
        for dw in self.decWords:
            if (" %s " % dw) in t:
                return MappedEntry(entry, "neemt af", 1)
        return None

class SurviveMapping:
    words = ["overleeft", "gewond"]

    def map(self, entry):
        t = " %s " % entry["title"].lower()
        for w in self.words:
            if (" %s " % w) in t:
                return MappedEntry(entry, "overleeft", 1)
        if re.search("ontsnapt aan ([a-zA-Z]+)? letsel", t):
            return MappedEntry(entry, "overleeft", 1)
        return None

class PriceMapping:
    incWords = ["wordt duurder"]
    decWords = ["wordt goedkoper"]

    def map(self, entry):
        t = " %s " % entry["title"].lower()
        for iw in self.incWords:
            if (" %s " % iw) in t:
                return MappedEntry(entry, "duurder", 1)
        for dw in self.decWords:
            if (" %s " % dw) in t:
                return MappedEntry(entry, "goedkoper", 1)
        return None


class IdMapping:
    def map(self, entry):
        """Return the simplified form, or None"""
        return MappedEntry(entry, "berichten", 1)

mappings = [
    DeathTollMapping(),
    IncDecMapping(),
    PriceMapping(),
    SurviveMapping(),
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
        "duizend": 1000,
        "duizenden": 5000
    }
    for (word, value) in mapping.items():
        if word in s:
            s = s.replace(" %s " % word, str(value))
    return s

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


