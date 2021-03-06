import unittest
import parser as psr
import grammar as gmr


class TestState(unittest.TestCase):

    def test_incomplete(self):
        # Complete case.
        incomplete_state = psr.State(rule=gmr.Rule('S', ['VP']),
                                     span_start=0,
                                     span_stop=0,
                                     dot_position=0)
        self.assertTrue(incomplete_state.incomplete)

        # Incomplete case.
        complete_state = psr.State(rule=gmr.Rule('S', ['VP']),
                                   span_start=0,
                                   span_stop=0,
                                   dot_position=1)
        self.assertFalse(complete_state.incomplete)

    def test_next_category(self):
        # Complete case.
        state = psr.State(rule=gmr.Rule('S', ['VP']),
                          span_start=0,
                          span_stop=0,
                          dot_position=0)
        self.assertEqual('VP', state.next_category)

        # Incomplete case.
        state = psr.State(rule=gmr.Rule('S', ['VP']),
                          span_start=0,
                          span_stop=1,
                          dot_position=1)
        self.assertEqual('', state.next_category)


class TestEarleyParser(unittest.TestCase):

    def test_parse(self):
        grammar = gmr.Grammar(
            gmr.Rule('S', ['VP']),
            gmr.Rule('VP', ['V', 'NP']),
            gmr.Rule('NP', ['Det', 'Nominal']),
            gmr.Rule('Det', ['that'], preterminal=True),
            gmr.Rule('Nominal', ['flight'], preterminal=True),
            gmr.Rule('V', ['Book'], preterminal=True)
        )

        words = ['Book', 'that', 'flight']

        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)

        self.assertEqual([['S', ['VP', ['V', 'Book'], ['NP', ['Det', 'that'], ['Nominal', 'flight']]]]],
                         trees)

    def test_multiple_parses(self):
        grammar = gmr.Grammar(
            gmr.Rule('N', ['I'], preterminal=True),
            gmr.Rule('V', ['made'], preterminal=True),
            gmr.Rule('N', ['her'], preterminal=True),
            gmr.Rule('V', ['duck'], preterminal=True),
            gmr.Rule('N', ['duck'], preterminal=True),
            gmr.Rule('S', ['N', 'V', 'N', 'V']),
            gmr.Rule('S', ['N', 'V', 'N', 'N'])
        )
        words = ['I', 'made', 'her', 'duck']
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(2, len(trees))
        self.assertEqual([
            ['S', ['N', 'I'], ['V', 'made'], ['N', 'her'], ['V', 'duck']],
            ['S', ['N', 'I'], ['V', 'made'], ['N', 'her'], ['N', 'duck']]
        ], trees)

    def test_ambiguity(self):
        grammar = gmr.Grammar(
            gmr.Rule('S', ['NP', 'VP']),
            gmr.Rule('NP', ['Det', 'Nominal']),
            gmr.Rule('NP', ['Det', 'Nominal', 'PP']),
            gmr.Rule('NP', ['Nominal']),
            gmr.Rule('VP', ['VP', 'PP']),
            gmr.Rule('VP', ['V', 'NP']),
            gmr.Rule('PP', ['Prep', 'NP']),
            gmr.Rule('Det', ['a'], preterminal=True),
            gmr.Rule('Nominal', ['I'], preterminal=True),
            gmr.Rule('Nominal', ['man'], preterminal=True),
            gmr.Rule('Nominal', ['telescope'], preterminal=True),
            gmr.Rule('V', ['saw'], preterminal=True),
            gmr.Rule('Prep', ['with'], preterminal=True)
        )
        words = ['I', 'saw', 'a', 'man', 'with', 'a', 'telescope']
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(2, len(trees))
        self.assertEqual([
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
        ], trees)

    def test_no_parses(self):
        grammar = gmr.Grammar(
            gmr.Rule('N', ['Nothing'], preterminal=True)
        )
        words = ['Something']
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(0, len(trees))
        self.assertEqual([], trees)

    def test_empty_grammar(self):
        grammar = gmr.Grammar()
        words = ['Something']
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(0, len(trees))
        self.assertEqual([], trees)

    def test_empty_words(self):
        grammar = gmr.Grammar(
            gmr.Rule('N', ['Nothing'], preterminal=True)
        )
        words = []
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(0, len(trees))
        self.assertEqual([], trees)

    def test_regex_rule(self):
        grammar = gmr.Grammar(
            gmr.Rule('S', [gmr.Regex(r'[a-z]')], preterminal=True)
        )
        words = ['hello']
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual(1, len(trees))
        self.assertEqual([['S', 'hello']], trees)

    def test_programming_language_parsing(self):
        grammar = gmr.Grammar(
            gmr.Rule('program', ['variable', 'operator', 'value']),
            gmr.Rule('variable', [gmr.Regex(r'x')], preterminal=True),
            gmr.Rule('operator', [gmr.Regex(r'[+\-=*/]')], preterminal=True),
            gmr.Rule('value', [gmr.Regex(r'\d+')], preterminal=True),
            distinguished_symbol='program'
        )
        words = ['x', '=', '599993949']
        parser = psr.EarleyParser(grammar)
        trees = parser.parse(words)
        self.assertEqual([['program',
                               ['variable', 'x'],
                               ['operator', '='],
                               ['value', '599993949']
                           ]
        ], trees)


