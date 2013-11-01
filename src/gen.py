# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-

import feedparser
from jinja2 import Template
import codecs
import os
import pickle
import re
import datetime
from mapping import performMapping
import json


nuFeeds = [
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Algemeen",
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Economie",
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Internet",
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Opmerkelijk",
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Wetenschap",
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Gezondheid"
    ]



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

def render(context, template, output):
    with codecs.open(template, 'rb', 'utf-8') as templateHandle:
        with codecs.open(output, 'wb', 'utf-8') as outputHandle:
            t = Template(templateHandle.read())
            outputHandle.write(t.render(**context))


def loadEntries():
    entries = []
    for feedUrl in nuFeeds:
        try:
            feed = feedparser.parse(feedUrl)
            entries.extend(feed["entries"])
        except Exception as e:
            print("Failed to download feed from %s" % feedUrl)
    return entries

def entryId(entry):
    return re.sub("^http://(www\\.)?nu\\.nl/[a-z]+/", "", entry["id"])


def main():
    print("Start (of zoals de Russen zeggen 'начало'):", datetime.datetime.now())
    db = Db()
    db.open()
    entries = loadEntries()
    dropKeys = ["summary", "tags", "summary_detail", "title_detail", "links", 'related']
    print("Loaded %i new entries" % len(entries))
    for entry in entries:
        for k in dropKeys:
            if entry.has_key(k):
                del entry[k]
        db.addOrUpdate(entryId(entry), entry)

    mappedEntries = performMapping(db.find())

    print("Mapped to %i entries" % len(mappedEntries))
    haveBeenMapped = [entryId(m.entry()) for m in mappedEntries]

    for e in db.find():
        if haveBeenMapped.count(entryId(e)) <= 1:
            print("Not mapped enough:", e["title"])

    #Create buckets and place the entries in buckets
    now = datetime.datetime.now()
    nPoints = 1280
    buckets = [{"time": now - datetime.timedelta(hours=i)} for i in range(nPoints)]
    buckets.reverse()

    oldestUsedTime = buckets[0]["time"]
    print("Oldest used time:", oldestUsedTime)

    graphs = {}
    idents = list(set([e.ident() for e in mappedEntries]))
    idents.sort()
    #Start a graph for each ident
    for i in idents:
        graphs[i] = [0] * len(buckets)

    #One bucket per hour, add counts to the buckets
    for entry in mappedEntries:
        published = entry.published()
        if published < oldestUsedTime:
            db.remove(entryId(entry.entry()))
            continue
        for bucketIndex in range(nPoints):
            timeDiff = abs(published - buckets[bucketIndex]['time'])
            if timeDiff < datetime.timedelta(hours=1):
                graphs[entry.ident()][bucketIndex] += entry.count()
                break

    thisWeekPerIdent = {}
    for i in idents:
        thisWeekPerIdent[i] = []
    thisWeek = now - datetime.timedelta(days=7)
    for entry in mappedEntries:
        published = entry.published()
        if published > thisWeek:
            thisWeekPerIdent[entry.ident()].append(entry.entry())
    for i in idents:
        thisWeekPerIdent[i].sort(key=lambda x: x["title"])


    for i in idents:
        print(i, graphs[i][-5:])

    # Collapse entries into dict-dict-dict-href
    with codecs.open("www/graphs.json", 'wb', 'utf-8') as jsonHandle:
        json.dump(graphs, jsonHandle, separators=(',',':'))

    render({}, 'src/templates/app.js', 'www/app.js')
    render({"idents": idents, 'thisWeekPerIdent': thisWeekPerIdent, 'modified': now.strftime("%Y-%m-%d")}, 'src/templates/index.html', 'www/index.html')
    db.close()
    print("End:", datetime.datetime.now())

# Use http://mbostock.github.io/d3/talk/20111018/tree.html
if __name__ == "__main__":
    main()

