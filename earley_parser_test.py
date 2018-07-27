import unittest
import parser as psr


class TestState(unittest.TestCase):

    def test_incomplete(self):
        # Complete case.
        incomplete_state = psr.State(rule=psr.Rule('S', ['VP']),
                                     span_start=0,
                                     span_stop=0,
                                     dot_position=0)
        self.assertTrue(incomplete_state.incomplete)

        # Incomplete case.
        complete_state = psr.State(rule=psr.Rule('S', ['VP']),
                                   span_start=0,
                                   span_stop=0,
                                   dot_position=1)
        self.assertFalse(complete_state.incomplete)

    def test_next_category(self):
        # Complete case.
        state = psr.State(rule=psr.Rule('S', ['VP']),
                          span_start=0,
                          span_stop=0,
                          dot_position=0)
        self.assertEqual(state.next_category, 'VP')

        # Incomplete case.
        state = psr.State(rule=psr.Rule('S', ['VP']),
                          span_start=0,
                          span_stop=1,
                          dot_position=1)
        self.assertEqual(state.next_category, '')


class TestEarleyParser(unittest.TestCase):

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

        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)

        self.assertEqual(trees,
                         [['S', ['VP', ['V', 'Book'], ['NP', ['Det', 'that'], ['Nominal', 'flight']]]]])

    def test_multiple_parses(self):
        grammar = [
            psr.Rule('N', ['I'], preterminal=True),
            psr.Rule('V', ['made'], preterminal=True),
            psr.Rule('N', ['her'], preterminal=True),
            psr.Rule('V', ['duck'], preterminal=True),
            psr.Rule('N', ['duck'], preterminal=True),
            psr.Rule('S', ['N', 'V', 'N', 'V']),
            psr.Rule('S', ['N', 'V', 'N', 'N'])
        ]
        words = ['I', 'made', 'her', 'duck']
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(len(trees), 2)
        self.assertEqual(trees, [
            ['S', ['N', 'I'], ['V', 'made'], ['N', 'her'], ['V', 'duck']],
            ['S', ['N', 'I'], ['V', 'made'], ['N', 'her'], ['N', 'duck']]
        ])

    def test_ambiguity(self):
        grammar = [
            psr.Rule('S', ['NP', 'VP']),
            psr.Rule('NP', ['Det', 'Nominal']),
            psr.Rule('NP', ['Det', 'Nominal', 'PP']),
            psr.Rule('NP', ['Nominal']),
            psr.Rule('VP', ['VP', 'PP']),
            psr.Rule('VP', ['V', 'NP']),
            psr.Rule('PP', ['Prep', 'NP']),
            psr.Rule('Det', ['a'], preterminal=True),
            psr.Rule('Nominal', ['I'], preterminal=True),
            psr.Rule('Nominal', ['man'], preterminal=True),
            psr.Rule('Nominal', ['telescope'], preterminal=True),
            psr.Rule('V', ['saw'], preterminal=True),
            psr.Rule('Prep', ['with'], preterminal=True)
        ]
        words = ['I', 'saw', 'a', 'man', 'with', 'a', 'telescope']
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(len(trees), 2)
        self.assertEqual(trees, [
            # ... saw ... with a telescope
            ['S', ['NP', ['Nominal', 'I']],
                  ['VP', ['VP', ['V', 'saw'], ['NP', ['Det', 'a'], ['Nominal', 'man']]],
                         ['PP', ['Prep', 'with'], ['NP', ['Det', 'a'], ['Nominal', 'telescope']]
                         ]
                  ]
            ],
            # ... man with a telescope
            ['S', ['NP', ['Nominal', 'I']],
                  ['VP', ['V', 'saw'],
                         ['NP', ['Det', 'a'], ['Nominal', 'man'],
                                ['PP', ['Prep', 'with'], ['NP', ['Det', 'a'], ['Nominal', 'telescope']]]
                         ]
                  ]
            ]
        ])

    def test_no_parses(self):
        grammar = [
            psr.Rule('N', ['Nothing'], preterminal=True)
        ]
        words = ['Something']
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(len(trees), 0)
        self.assertEqual(trees, [])

    def test_empty_grammar(self):
        grammar = []
        words = ['Something']
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(len(trees), 0)
        self.assertEqual(trees, [])

    def test_empty_words(self):
        grammar = [
            psr.Rule('N', ['Nothing'], preterminal=True)
        ]
        words = []
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(len(trees), 0)
        self.assertEqual(trees, [])
