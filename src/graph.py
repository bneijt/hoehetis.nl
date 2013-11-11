# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-

from jinja2 import Template
import codecs
import os
import pickle
import entries as E
import datetime
import re
import time
import json

class Db:
    def open(self):
        if os.path.exists('db.pkl'):
            with open("db.pkl", "rb") as f:
                self.contents = pickle.load(f)
        else:
                self.contents = {}
    def close(self):
        with open("db.pkl", "wb") as f:
            pickle.dump(self.contents, f, pickle.HIGHEST_PROTOCOL)

    def addOrUpdate(self, ident, value):
        self.contents[ident] = value
    def remove(self, ident):
        if ident in self.contents:
            del self.contents[ident]
    def find(self):
        return self.contents.values()


def normalize(t):
    t = " %s " % t
    t = re.sub("\\s'(\\S)",  "' \\1", t)
    t = re.sub("(\\S)'\\s",  "\\1 '", t)
    t = re.sub("\\s\\s", " ", t)
    return t.strip()

def normalizeEntry(entry):
    return normalize(entry['title'])

def publishedDateOf(entry):
        return  datetime.datetime.fromtimestamp(time.mktime(entry["published_parsed"]))

def main():
    print("Start (of zoals de Russen zeggen 'начало'):", datetime.datetime.now())
    db = Db()
    db.open()

    entries = db.find()
    print("Loaded %i entries" % len(entries))
    titles = map(normalizeEntry, entries)

    edges = {}
    for title in titles:
        for sublist in sublistsOf(title):
            center = sublist.center()
            surr = sublist.head() + sublist.tail()
            edges[surr].append(center)
            edges[center].append(surr)

    #We now have connections between all word sublists of each title
    #We can now use each edge as a possible category and add titles
    # to them.
    #
    # db.close()
    print("End:", datetime.datetime.now())

if __name__ == "__main__":
    main()

