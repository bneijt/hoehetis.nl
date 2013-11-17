# -*- coding: utf-8 -*-
import random
import unittest
import gen as G
import datetime

class GraphBased(unittest.TestCase):
# snellere
# Kamer wil spoediger snellere treinen op HSL
# Geen treinen bij Leiden na vondst mogelijke bom WOII
    def test_shouldSeeTrains(self):
        entries = [
            {"title": "Kamer wil spoediger snellere treinen op HSL"},
            {"title": "Geen treinen bij Leiden na vondst mogelijke bom WOII"}
        ]
        titles = G.getNormalizedTitles(entries)
        keywords = G.determinekeywordsFrom(titles)
        keywords.sort(key=G.Guess.prob)
        self.assertEqual(keywords[-1].word, "treinen")

    def test_selectWordWithOffsetFromIn(self):
        entries = [
            {"title": "Kamer wil spoediger snellere treinen op HSL"},
            {"title": "Geen treinen bij Leiden na vondst mogelijke bom WOII"}
        ]
        titles = G.getNormalizedTitles(entries)
        ws = G.selectWordWithOffsetFromIn("treinen", 1, titles)
        self.assertEqual(ws, ["op", "bij"])
        ws = G.selectWordWithOffsetFromIn("treinen", -1, titles)
        self.assertEqual(ws, ["snellere", "Geen"])

    def test_determineSynoymsForWord(self):
        entries = [
            {"title": "Kamer wil spoediger snellere treinen op HSL"},
            {"title": "Geen treinen bij Leiden na vondst mogelijke bom WOII"}
        ]
        titles = G.getNormalizedTitles(entries)
        firstTitleWords = titles[0].split(" ")
        synonyms = G.determineSynoymsForWord(titles, firstTitleWords, 1)
        self.assertEqual(synonyms[0].word, "wil") #No synonyms detectable

        synonyms = G.determineSynoymsForWord(titles, firstTitleWords, 3)
        synWords = [s.word for s in synonyms]
        synWords.sort()
        self.assertEqual(synWords, ["Geen", "snellere"])

        synonyms = G.determineSynoymsForWord(titles, firstTitleWords, 4)
        synWords = [s.word for s in synonyms]
        synWords.sort()
        self.assertEqual(synWords, ["treinen"])

        synonyms = G.determineSynoymsForWord(titles, firstTitleWords, 5)
        synWords = [s.word for s in synonyms]
        synWords.sort()
        self.assertEqual(synWords, ["bij", "op"])

if __name__ == '__main__':
    unittest.main()
