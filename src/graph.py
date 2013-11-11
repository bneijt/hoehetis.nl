# -*- coding: utf-8 -*-# -*- coding: utf-8 -*-

from jinja2 import Template
import codecs
import os
import pickle
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
    t = re.sub("\\s'(\\S)",  " ' \\1", t)
    t = re.sub("(\\S)'\\s",  "\\1 ' ", t)
    t = re.sub("\\s\\s", " ", t)
    return t.strip()

def normalizeEntry(entry):
    return normalize(entry['title'])

def publishedDateOf(entry):
    return  datetime.datetime.fromtimestamp(time.mktime(entry["published_parsed"]))
def publishedThisMonth(entries):
    oldestAllowed = datetime.date.today() - datetime.timedelta(days=7*4)
    for idx, entry in enumerate(entries):
        if publishedDateOf(entry).date() > oldestAllowed:
            yield (idx, entry)

class Guess(object):
    """docstring for Guess"""
    def __init__(self, word, freq, normalization):
        super(Guess, self).__init__()
        assert isinstance(word, type(""))
        assert isinstance(freq, type(1))
        assert isinstance(normalization, type(1))
        self.word = word
        self.freq = freq
        self.normalization = normalization
    def __str__(self):
        return "Guess: \"%s\" (%i/%i)" % (self.word, self.freq, self.normalization)
    def sameWordAs(self, other):
        return self.word == other.word
    def add(self, other):
        if other.freq == 0:
            return
        self.freq = self.freq * other.normalization
        self.freq += other.freq * self.normalization
        self.normalization = other.normalization * self.normalization
    def prob(self):
        return self.freq / self.normalization

def determinekeywordsFrom(titles):
    #keywords are not to frequent, but still frequent words.
    #Each keyword is given a probability of it being a real keyword
    keywords = {}
    for title in titles:
        words = title.split(" ")
        for word in words:
            if word in keywords:
                keywords[word] += 1
            else:
                keywords[word] = 1
    #Normalize keywords frequency count to create probability?
    return [Guess(word, count, len(keywords)) for word, count in keywords.items()]

def selectWordWithOffsetFromIn(word, offset, titles):
    def sel(title):
        words = title.split(" ")
        if word not in words:
            return None
        idx = words.index(word) - offset
        if idx >= 0 and idx < len(words):
            return words[idx]
        return None

    containing = [sel(title) for title in titles]
    while None in containing:
        containing.remove(None)
    return containing

def listToGuess(l):
    """Return the guess of each entry based on it's count"""
    return [Guess(entry, l.count(entry), len(l)) for entry in set(l)]



def determineSynoymsForWord(titles, titleWords, wordIndex):
    #Determine which other words are possible based on surrounding words
    #Take the word after the word given in other titles
    alternatives = []
    if wordIndex > 0:
        #Not the first word
        wordBefore = titleWords[wordIndex -1]
        alternatives.extend(selectWordWithOffsetFromIn(wordBefore, 1, titles))
    if wordIndex < len(titleWords) -1:
        #Not the last word
        wordAfter = titleWords[wordIndex +1]
        alternatives.extend(selectWordWithOffsetFromIn(wordAfter, -1, titles))
    return listToGuess(alternatives)


def determineSynonymsFor(titles):
    #For each title, create replacable entries
    #We want :: titles -> [title in words] -> w -> [w]

    permuableTitles = []
    for title in titles:
        words = title.split(" ")
        permuableTitle = []
        for wordIndex in range(len(words)):
            alternativeWords = determineSynoymsForWord(titles, words, wordIndex)
            permuableTitle.append(alternativeWords)
        permuableTitles.append(permuableTitle)
    return permuableTitles

def titleMatchesKeyword(title, keywordGuess):
    #A title matches the keyword by summing all the guesses in the
    #title that match the keyword and multiplying by the keyword's
    # chance of being a keyword
    total = Guess(keywordGuess.word, 0, 1)
    for w in title:
        for sameWord in filter(lambda x: x.sameWordAs(keywordGuess), w):
            total.add(sameWord)
    return total

class GroupedEntry(object):
    """docstring for GroupedEntry"""
    def __init__(self, entry):
        super(GroupedEntry, self).__init__()
        self.entry = entry
        self.keywords = []

def groupAllEntriesForThisMonth(entries, synonyms, keywords):
    #Find chance of every keyword matching a title, ordered by probability
    groupedEntries = []
    for idx, entry in publishedThisMonth(entries):
        ge = GroupedEntry(entry)
        synonym = synonyms[idx]
        for keyword in keywords:
            tkm = titleMatchesKeyword(synonym, keyword)
            if tkm.freq > 0:
                ge.keywords.append(tkm)
        ge.keywords.sort(key = Guess.prob)
        groupedEntries.append(ge)
    return groupedEntries

def orderAllKeywordsForGroupedEntries(groupedEntries):
    """Take the keywords for each of the grouped entries and
    create a single list of most probable keywords. Combine
    them on words into"""
    allMatchedKeywords = {}
    for ge in groupedEntries:
        for kw in ge.keywords:
            if kw.word in allMatchedKeywords:
                allMatchedKeywords[kw.word].add(kw)
            else:
                allMatchedKeywords[kw.word] = Guess(kw.word, kw.freq, kw.normalization)
    return sorted(allMatchedKeywords.values(), key=Guess.prob)

def main():
    print("Start (of zoals de Russen zeggen 'начало'):", datetime.datetime.now())
    db = Db()
    db.open()

    entries = list(db.find())
    print("Loaded %i entries" % len(entries))
    titles = list(map(normalizeEntry, entries))

    keywords = determinekeywordsFrom(titles)

    synonyms = determineSynonymsFor(titles)


    groupedEntries = groupAllEntriesForThisMonth(entries, synonyms, keywords)

    ge = groupedEntries[0]
    print("Title:", ge.entry['title'])
    for t in ge.keywords:
        print(t)

    #Take the 10 most probable keywords from these titles
    topTenKeywords = orderAllKeywordsForGroupedEntries(groupedEntries)[:10]

    print ("Top 10 keywords:")
    for kw in topTenKeywords:
        print(kw)


    # db.close()
    print("End:", datetime.datetime.now())

if __name__ == "__main__":
    main()

