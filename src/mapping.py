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
    deadWords = ["zelfmoord", "omgekomen", "omgebracht", "dode", "gedood", "overleden", "stierf", "moord"]
    def simple(self, entry):
        fingerprint = entry["title"]
        fingerprint = fingerprint[0:1].lower() + fingerprint[1:]
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
        match = re.search("([0-9]+)\\s+([a-z]+\\s)?(dode|doden|overledenen|gestorven|omgekomen|gedood)", fingerprint)
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


class IncMapping:
    ident = "neemt toe"
    incWords = ["neemt toe",
        "vaker",
        "winnen terrein",
        "stijgt",
        "stijgen",
        "verbeteren kwaliteit",
        "gaan hoge vlucht nemen",
        "trekt aan",
        "nieuwe regels",
        "sneller"]
    incRegex = ["meer [a-z]+", "toename [a-z]+", "stijgen met [a-z0-9]+"]

    def map(self, entry):
        t = " %s " % entry["title"].lower()
        t = t.replace("'", " ' ")
        for ir in self.incRegex:
            if re.search(" %s " % ir, t):
                return MappedEntry(entry, self.ident, 1)
        for iw in self.incWords:
            if (" %s " % iw) in t:
                return MappedEntry(entry, self.ident, 1)
        return None

class DecMapping:
    ident = "neemt af"
    decWords = ["neemt af", "minder vaak", "verliezen terrein", "daalt", "dalen", "verslechten kwaliteit", "niet langer", "laagste peil sinds"]
    decRegex = ["minder [a-z]+", "[a-z]+vermindering", "schrapt [a-z0-9]+ banen"]

    def map(self, entry):
        t = " %s " % entry["title"].lower()
        for dr in self.decRegex:
            if re.search(" %s " % dr, t):
                return MappedEntry(entry, self.ident, 1)
        for dw in self.decWords:
            if (" %s " % dw) in t:
                return MappedEntry(entry, self.ident, 1)
        return None


class SurviveMapping:
    ident = "overleeft"
    words = ["overleeft", "gewond"]

    def map(self, entry):
        t = " %s " % entry["title"].lower()

        match = re.search("([0-9]+)\\s+(gewonde|gewonden)", t)
        if match != None:
            return MappedEntry(
                entry,
                self.ident,
                int(round(float(match.group(1))))
            )

        for w in self.words:
            if (" %s " % w) in t:
                return MappedEntry(entry, self.ident, 1)
        if re.search("ontsnapt aan ([a-zA-Z]+)? letsel", t):
            return MappedEntry(entry, self.ident, 1)
        return None

class IncPriceMapping:
    ident = "duurder"
    incWords = ["duurder"]

    def map(self, entry):
        t = " %s " % entry["title"].lower()
        t = t.replace("'", " ' ")
        for iw in self.incWords:
            if (" %s " % iw) in t:
                return MappedEntry(entry, self.ident, 1)
        return None

class DecPriceMapping:
    ident = "goedkoper"
    decWords = ["goedkoper"]

    def map(self, entry):
        t = " %s " % entry["title"].lower()
        t = t.replace("'", " ' ")
        for dw in self.decWords:
            if (" %s " % dw) in t:
                return MappedEntry(entry, self.ident, 1)
        return None

class IdMapping:
    def map(self, entry):
        """Return the simplified form, or None"""
        return MappedEntry(entry, "berichten", 1)

mappings = [
    DeathTollMapping(),
    IncMapping(),
    DecMapping(),
    IncPriceMapping(),
    DecPriceMapping(),
    SurviveMapping(),
    IdMapping()
]

def deHumanize(s):
    numbers = {
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
    orders = {
        "eerste": 1,
        "tweede": 2,
        "derde": 3,
        "vierde": 4,
        "vijfde": 5,
        "zesde": 6,
        "zevende": 7,
        "achtste": 8,
        "negende": 9,
        "tiende": 10
    }
    mapping = {}
    mapping.update(numbers)
    mapping.update(orders)
    for (word, value) in mapping.items():
        if word in s:
            s = s.replace(" %s " % word, " %s " % str(value))
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


