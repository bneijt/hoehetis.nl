# -*- coding: utf-8 -*-
import random
import unittest
import freq as F
import datetime

class IdentCreator(unittest.TestCase):

    def test_shouldNormalizeText(self):
        fromTo = [
            ("a", "a"),
            ("'a", "' a"),
            ("a'", "a '"),
            ("m'n", "m'n"),
        ]
        for ft in fromTo:
            self.assertEqual(F.normalize(ft[0]), ft[1])

    def test_shouldWorkWithSurroundingListGeneration(self):
        fromTo = [
            [(1, [1,2,3], 1), [1,2,3]],
            [(0, [1,2,3], 1), ["", 1, 2]],
            [(0, [1,2,3], 0), [1]],
        ]
        for ft in fromTo:
            self.assertEqual(F.surrounding(*ft[0]).value(), ft[1])
    def test_headTailShouldWork(self):
        a = F.Surrounding([1,2,3])
        self.assertEqual(a.head(), [1])
        self.assertEqual(a.center(), 2)
        self.assertEqual(a.tail(), [3])

        b = F.Surrounding([2])
        self.assertEqual(b.head(), [])
        self.assertEqual(b.center(), 2)
        self.assertEqual(b.tail(), [])

    def test_shouldWorkWithSurroundingCenter(self):
        fromTo = [
            [(1, [1,2,3], 1), 2],
            [(0, [1,2,3], 1), 1],
            [(0, [1,2,3], 0), 1],
        ]
        for ft in fromTo:
            self.assertEqual(F.surrounding(*ft[0]).center(), ft[1])
    def test_surroundShouldSupportStringMatching(self):
        fromTo = [
            (["how", "", "you"], "how banana you", True),
            (["how", "", "you"], "how banana yo", False),
            (["", "you", "doing"], "banana doing", True),
            (["1", "2", "3"], "1 2 3", True),
            (["1", "2", "3"], "1 4 3", True),
            (["1", "2", "3", "4", "5"], "x x x 1 2 3 4 5 6", True),
            (["1", "2", "3"], "x x x 1 4 2 1 2 3", True),
            (["how", "", "you"], "", False),
            (["how", "", "you"], "how word", False),
            (["how", "", "you"], "some word you", False),
            (["", "", "en"], "Brabantse krantenbezorgers verliezen baan", False),
            (["in", "Nederland", ""], "Bij invallen in Brabantse verliezen", True),
        ]
        for ft in fromTo:
            self.assertEqual(F.Surrounding(ft[0]).matchesString(ft[1]), ft[2], msg="Failed with example %s" % repr(ft))

if __name__ == '__main__':
    unittest.main()
