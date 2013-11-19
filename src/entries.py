import feedparser
import re
import os
import pickle

nuFeeds = [
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Algemeen",
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Economie",
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Internet",
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Opmerkelijk",
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Wetenschap",
    "http://www.nu.nl/deeplink_rss2/index.jsp?r=Gezondheid"
    ]

def download():
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

def loadEntries():
    entries = []
    for feedUrl in nuFeeds:
        try:
            feed = feedparser.parse(feedUrl)
            entries.extend(feed["entries"])
        except Exception as e:
            print("Failed to download feed from %s" % feedUrl)
    return entries


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
        stripped = {}
        keep = ['title', 'published_parsed', 'id', 'link']
        for k in keep:
            stripped[k] = value[k]
        self.contents[ident] = stripped

    def remove(self, ident):
        if ident in self.contents:
            del self.contents[ident]
    def removeOldestWhenOver(self, maxLength):
        while len(self.contents) > maxLength:
            maxEntry = min(self.contents.values(), key=lambda x: x['published_parsed'])
            del self.contents[entryId(maxEntry)]

    def find(self):
        return self.contents.values()

def updateDb(db):
    entries = loadEntries()
    #TODO make whitelist instead
    dropKeys = ["summary", "tags", "summary_detail", "title_detail", "links", 'related']
    print("Loaded %i new entries" % len(entries))
    for entry in entries:
        for k in dropKeys:
            if entry.has_key(k):
                del entry[k]
        db.addOrUpdate(entryId(entry), entry)

