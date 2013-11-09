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

def unique(el, hash):
    seen = set()
    return [x for x in seq if hash(x) not in seen and not seen.add(hash(x))]

def iterSublistPositonOfIn(needle, haystack):
    #TODO optimize
    for i in range(len(haystack)):
        if needle == haystack[i : i + len(needle)]:
            yield i
    return


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

def normalize(t):
    t = " %s " % t
    t = re.sub("\\s'(\\S)",  "' \\1", t)
    t = re.sub("(\\S)'\\s",  "\\1 '", t)
    t = re.sub("\\s\\s", " ", t)
    return t.strip()

def normalizeEntry(entry):
    return normalize(entry['title'])

def getOrEmptyString(idx, l):
    if idx < len(l):
        if idx >= 0:
            return l[idx]
    return ""

class Surrounding(object):
    """docstring for Surrounding"""
    def __init__(self, l):
        super(Surrounding, self).__init__()
        self._l = l
    def __str__(self):
        return "%ix \"%s\"" % (self.count, " ".join(self._l))
    def clone(self):
        return Surrounding(self._l[:])
    def hash(self):
        return " ".join(self._l)
    def center(self, value = None):
        if value != None:
            self._l[int(len(self._l)/2)] = value
        return self._l[int(len(self._l)/2)]
    def value(self):
        return self._l
    def head(self):
        return self._l[:int(len(self._l)/2)]
    def tail(self):
        return self._l[int(len(self._l)/2) + 1:]
    def centerInterchangableWith(self, other):
        return self.head() == other.head() and self.tail() == other.tail()
    def matchesString(self, title):
        titleWords = normalize(title).split(" ")
        head = self.head()[:]
        while '' in head:
            head.remove('')
        tail = self.tail()[:]
        while '' in tail:
            tail.remove('')
        for headMatchPos in iterSublistPositonOfIn(head, titleWords):
            startOfTail = headMatchPos + len(head) + 1
            if titleWords[startOfTail: startOfTail + len(tail)] == tail:
                return True
            if len(head) == 0:
                #If the head is empty, the match is only valid if the titleWords
                #match at the start of the list. So the first titlewords word
                # must be the center of the match
                break
        return False

def surrounding(idx, ws, offsetEitherWay):
    subList = [ws[idx]]
    for i in range(1, offsetEitherWay + 1):
        subList.insert(0, getOrEmptyString(idx - i, ws))
        subList.append(getOrEmptyString(idx + i, ws))
    return Surrounding(subList)

def sublistsFrom(words):
    sublists = []
    for idx, word in enumerate(words):
        # sublists.append(surrounding(idx, words, 0))
        sublists.append(surrounding(idx, words, 1))
        sublists.append(surrounding(idx, words, 2))
        sublists.append(surrounding(idx, words, 3))
    return sublists

def addCountsAndMakeUnique(sublists):
    counts = {}
    for s in sublists:
        s.count = 1
        k = s.hash()
        if k in counts:
            counts[k].count += s.count
        else:
            counts[s.hash()] = s
    return counts.values()

def publishedDateOf(entry):
        return  datetime.datetime.fromtimestamp(time.mktime(entry["published_parsed"]))
def main():
    print("Start (of zoals de Russen zeggen 'начало'):", datetime.datetime.now())
    db = Db()
    db.open()

    # entries = E.download()
    # dropKeys = ["summary", "tags", "summary_detail", "title_detail", "links", 'related']
    # print("Loaded %i new entries" % len(entries))
    # for entry in entries:
    #     for k in dropKeys:
    #         if entry.has_key(k):
    #             del entry[k]
    #     db.addOrUpdate(E.id(entry), entry)
    entries = db.find()
    print("Loaded %i entries" % len(entries))
    titles = map(normalizeEntry, entries)
    sublists = []
    for title in titles:
        words = title.split(' ')
        sublists.extend(sublistsFrom(words))

    sublists = list(addCountsAndMakeUnique(sublists))
    #We now have a list of sublists of all the titles
    #Each has a count of the number of times it's appeared
    #Now we should be able to determine probable exchange patterns: something x something
    # For each word in each title, determine the replacement probability for each other word
    # Replace by * and match everything if the graph looks ok
    exchangePatterns = {}
    for sublist in sublists:
        key = sublist.hash()
        if key not in exchangePatterns:
            exchangePatterns[key] = []
        for candidate in sublists:
            if candidate.hash() == key:
                continue
            if sublist.centerInterchangableWith(candidate):
                #We have found an interchange pattern
                exchangePatterns[key].append(candidate)

        #Filter empties
        if len(exchangePatterns[key]) == 0:
            del exchangePatterns[key]

    uniqueExchangePatterns = {}
    for key in exchangePatterns.keys():
        sp = exchangePatterns[key][0].clone()
        sp.center("")
        uniqueExchangePatterns[sp.hash()] = sp
    uniqueExchangePatterns = uniqueExchangePatterns.values()



    print(len(uniqueExchangePatterns))
    for p in uniqueExchangePatterns:
        p.matchCount = 0
    #A story should not end up in two catagories at the same time.
    #Any exchange pattern which cases this to happen should be removed
    # so for all the titles, if it matches two exchange patterns, destroy the exchange pattern
    for title in titles:
        matching = []
        for idx, pattern in enumerate(uniqueExchangePatterns):
            if pattern.matches(title):
                matching.append(idx)
                pattern.matchCount += 1
        if len(matching) > 1:
            for idx in matching:
                del uniqueExchangePatterns[idx]
    print(len(uniqueExchangePatterns))

    #Graphs
    graphs = {}
    idents = [" ".join(u.head() + ["X"] + u.tail()) for u in  uniqueExchangePatterns]
    #Start a graph for each ident
    now = datetime.date.today()

    nPoints = 7*4
    buckets = [{"date": now - datetime.timedelta(days=i)} for i in range(nPoints)]
    buckets.reverse()

    oldestUsedTime = buckets[0]["date"]
    for i in idents:
        graphs[i] = [0] * len(buckets)

    #One bucket per day, add counts to the buckets for eacht entry that matches
    for entry in entries:
        published = publishedDateOf(entry)
        if published.date() < oldestUsedTime:
            # db.remove(entryId(entry.entry()))
            continue
        title = entry["title"]
        ident = None
        for (idx, pattern) in enumerate(uniqueExchangePatterns):
            if pattern.matchesString(title):
                ident = idents[idx]
                break
        if ident == None:
            print("No match found for: ", title)
            continue
        #Find bucket to increment
        for bucketIndex, bucket in enumerate(buckets):
            if bucket['date'] == published:
                graphs[ident][bucketIndex] += 1
                break
    print(repr(graphs.keys()))
    for k in graphs.keys():
        print(k, graphs[k])

    with codecs.open("www/gchart.json", 'wb', 'utf-8') as jsonHandle:
        json.dump(graphs, jsonHandle, separators=(',',':'))

    render({
        "idents": idents,
        'modified': now.strftime("%Y-%m-%dT%H:%M%z")},
        'src/templates/gchart.html', 'www/gchart.html')
    # db.close()
    print("End:", datetime.datetime.now())

if __name__ == "__main__":
    main()

