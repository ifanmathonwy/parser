import unittest

import grammar as gmr

class TestRule(unittest.TestCase):

    def test_equality(self):
        first_rule = gmr.Rule('S', ['NP', 'VP'])
        second_rule = gmr.Rule('S', ['NP', 'VP'])
        third_rule = gmr.Rule('S', ['VP', 'NP'])
        self.assertEqual(first_rule, second_rule)
        self.assertNotEqual(first_rule, third_rule)

class TestGrammar(unittest.TestCase):

    def test_initializer(self):
        grammar = gmr.Grammar(gmr.Rule('S', ['VP']),
                              gmr.Rule('VP', ['V']),
                              gmr.Rule('V', ['initialize'], preterminal=True))
        self.assertIn(gmr.Rule('S', ['VP']), grammar)
        self.assertIn(gmr.Rule('VP', ['V']), grammar)
        self.assertIn(gmr.Rule('V', ['initialize'], preterminal=True), grammar)
        self.assertEqual(3, len(grammar))

class TestRegex(unittest.TestCase):

    def test_equality(self):
        reg = gmr.Regex(r'hello')
        self.assertEqual('hello', reg)