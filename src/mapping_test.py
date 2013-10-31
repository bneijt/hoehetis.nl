# -*- coding: utf-8 -*-
import random
import unittest
import mapping as M
import datetime

class TestRegexMatcher(unittest.TestCase):

    def test_shouldCollapseNumbers(self):
        # make sure the shuffled sequence does not lose any elements
        a = {"title": "40 doden in bosnie"}
        b = {"title": "10 doden in turkije"}
        r = M.performMapping([a,b])
        self.assertEqual(r[0].ident(), "doden")
        self.assertEqual(r[0].count(), 40)

    def test_shouldMapManWithKnife(self):
        a = {"title": "Man met mes in schedel ontsnapt aan blijvend letsel"}
        b = {"title": "Man met mes in schedel ontsnapt aan bli3jvend letsel"}
        self.assertNotEqual(M.SurviveMapping().map(a), None)
        self.assertEqual(M.SurviveMapping().map(b), None)


if __name__ == '__main__':
    unittest.main()
