

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
    feed = loadFeed()
    entries = [Entry(entry) for entry in feed['entries']]

    newEntries = []
    while id(entries) != id(newEntries):
        print("Mapping %i entries" % len(entries))
        newEntries = performMapping(entries)

    # Collapse entries into dict-dict-dict-href
    render({"entries": entries}, 'templates/index.html', '../www/index.html')

if __name__ == "__main__":
    main()

