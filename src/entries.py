import feedparser
import re

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

def id(entry):
    return re.sub("^http://(www\\.)?nu\\.nl/[a-z]+/", "", entry["id"])
