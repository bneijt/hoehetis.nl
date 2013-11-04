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

    def test_shouldMatchMoreSomething(self):
        examples = [
            "Meer zieken door toename voedselinfecties",
            "Autoverkopen stijgen met ruim 37 procent",
            "Minder zieken door toename voedselinfecties",
            "Groei Chinese dienstensector trekt aan",
            "'Cyberverzekeringen gaan hoge vlucht nemen'",
            "'Toezichthouders schaars door nieuwe regels'",
            "'Bedrijven betalen rekeningen sneller'",
        ]

        m = M.IncMapping()
        for exampleTitle in examples:
            example = {"title": exampleTitle}
            me = m.map(example)
            self.assertFalse(me is None, msg="Could not find more in '%s'" % example['title'])
            self.assertEqual(me.ident(), m.ident)

    def test_shouldMatchMoreExpensive(self):
        examples = [
            ({"title": "'Beneluxtrein wordt stuk duurder'"}, "duurder")
        ]

        m = M.PriceMapping()
        for example in examples:
            self.assertEqual(m.map(example[0]).ident(), example[1])

    def test_shouldMatchLessSomething(self):
        examples = [
            {"title": "Minder zieken door toename voedselinfecties"},
            {"title": "'Aangever' Robert M. wil strafvermindering"},
            {"title": "UPC schrapt 75 banen in Nederland"},
            {"title": "'Rabobank niet langer betrouwbaarste bank'"},
        ]

        m = M.DecMapping()
        for example in examples:
            me = m.map(example)
            self.assertFalse(me is None, msg="Could not find less something in '%s'" % example['title'])
            self.assertEqual(me.ident(), m.ident)
            self.assertEqual(me.ident(), m.ident)

    def test_shouldSeeDeadPeople(self):
        cases = [
            ({"title": "Agenten gewond bij zelfmoord man in Helmond"}, 1),
            ({"title": "92 migranten omgekomen in woestijn Niger"}, 92),
            ({"title": "Handelaar drie jaar cel in om 140 dode dieren"}, 140),
            ({"title": "Derde dode door herfststorm"}, 3),
            ({"title": "'Fransen in koelen bloede omgebracht in Mali'"}, 1),
            ({"title": "Dode door ongeluk op spoorwegovergang"}, 1),
            ({"title": "'Fransen in koelen bloede omgebracht in Mali'"}, 1),
            ({"title": "Regisseur Leen Timp (92) overleden"}, 1),
            ({"title": "'Toetanchamon stierf mogelijk door botsing'"}, 1),
            ({"title": "OM eist achttien jaar voor moord Schoorl"}, 1),
        ]

        im = M.DeathTollMapping()
        for case in cases:
            me = im.map(case[0])
            self.assertFalse(me is None, msg="Could not find dead people in '%s'" % case[0]['title'])
            self.assertEqual(me.ident(), "doden")
            self.assertEqual(me.count(), case[1])

    def test_shouldSeeSurvival(self):
        examples = [
            ({"title": "Agenten gewond bij zelfmoord man in Helmond"}, 1),
            ({"title": "36 gewonden bij busongeluk Muiden"}, 36),
        ]

        m = M.SurviveMapping()
        for example in examples:
            i = m.map(example[0])
            self.assertEqual(i.ident(), "overleeft")
            self.assertEqual(i.count(), example[1])

if __name__ == '__main__':
    unittest.main()
