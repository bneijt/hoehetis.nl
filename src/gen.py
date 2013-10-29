

import feedparser
from jinja2 import Template
import codecs
import os
import pickle
import re
from mapping import Entry, performMapping

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

nuNlAlgemeen = "http://www.nu.nl/feeds/rss/algemeen.rss"

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

    def find(self):
        return self.contents.values()

def render(context, template, output):
    with codecs.open(template, 'rb', 'utf-8') as templateHandle:
        with codecs.open(output, 'wb', 'utf-8') as outputHandle:
            t = Template(templateHandle.read())
            outputHandle.write(t.render(**context))

def loadFeed():
    if not os.path.exists("feed.pkl"):
        feed = feedparser.parse(nuNlAlgemeen)
        with open("feed.pkl", "wb") as f:
            pickle.dump(feed, f, pickle.HIGHEST_PROTOCOL)
        return feed
    else:
        with open("feed.pkl", "rb") as f:
            feed = pickle.load(f)
            return feed


def main():
    db = Db()
    db.open()
    feed = loadFeed()
    entries = feed['entries']
    for entry in entries:
        db.addOrUpdate(entry['id'], entry)


    mappedEntries = performMapping(db.find())
    print("Mapped to %i entries" % len(mappedEntries))
    print (mappedEntries.keys())
    # table = tableFromEntries(entries)

    # Collapse entries into dict-dict-dict-href

    render({"idents": mappedEntries.keys(), 'mappedEntries': mappedEntries}, 'templates/index.html', '../www/index.html')
    db.close()

# Use http://mbostock.github.io/d3/talk/20111018/tree.html
if __name__ == "__main__":
    main()

