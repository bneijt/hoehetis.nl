# -*- coding: utf-8 -*-
import random
import unittest
import gen as G
import datetime

class IdentCreator(unittest.TestCase):

    def test_shouldCreateIdent(self):
        a = {"id": "http://www.nu.nl/buitenland/3616160/index.html"}
        b = {"id": "http://www.nu.nl/algemeen/3616160/index.html"}
        self.assertEqual(G.entryId(a), G.entryId(b))

if __name__ == '__main__':
    unittest.main()
