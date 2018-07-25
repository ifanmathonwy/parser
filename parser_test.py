import unittest

import parser as psr


class TestParser(unittest.TestCase):

    def test_parse(self):
        grammar = [
            psr.Rule('S', ['VP']),
            psr.Rule('VP', ['V', 'NP']),
            psr.Rule('NP', ['Det', 'Nominal']),
            psr.Rule('Det', ['that'], preterminal=True),
            psr.Rule('Nominal', ['flight'], preterminal=True),
            psr.Rule('V', ['Book'], preterminal=True)
        ]

        words = ['Book', 'that', 'flight']

        parser = psr.Parser(grammar)
        trees = parser.parse(words)

        self.assertEqual(trees,
                         [['GAMMA', ['S', ['VP', ['V', 'Book'], ['NP', ['Det', 'that'], ['Nominal', 'flight']]]]]])
