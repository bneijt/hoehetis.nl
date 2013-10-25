import random
import unittest
import mapping as M

class TestRegexMatcher(unittest.TestCase):

    def test_shouldCollapseNumbers(self):
        # make sure the shuffled sequence does not lose any elements
        a = {"title": "40 doden in bosnie"}
        b = {"title": "10 doden in turkije"}
        r = M.performMapping([M.Entry(a),M.Entry(b)])
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0].title(), "50 doden")


if __name__ == '__main__':
    unittest.main()
