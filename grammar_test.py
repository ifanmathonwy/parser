import unittest

import grammar as gmr

class TestGrammar(unittest.TestCase):

    def test_initializer(self):
        grammar = gmr.Grammar(gmr.Rule('S', ['VP']),
                              gmr.Rule('VP', ['V']),
                              gmr.Rule('V', ['initialize'], preterminal=True))
        self.assertIn(gmr.Rule('S', ['VP']), grammar)
        self.assertIn(gmr.Rule('VP', ['V']), grammar)
        self.assertIn(gmr.Rule('V', ['initialize'], preterminal=True), grammar)
        self.assertEqual(3, len(grammar))
