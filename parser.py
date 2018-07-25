"""Heavily based on Jurafsky and Martin. Great book.

"""

class Rule:
    def __init__(self, lhs, rhs, preterminal=False):
        self.lhs = lhs
        self.rhs = rhs
        self.preterminal = preterminal

    def __repr__(self):
        return '{} -> {}'.format(self.lhs, ' '.join(self.rhs))

class State:
    def __init__(self, rule, span_start, span_stop, dot_position, previous_states=None):
        """Dot position indexes interstices, starting from 0."""
        self.rule = rule
        self.span_start = span_start
        self.span_stop = span_stop
        self.dot_position = dot_position
        if previous_states:
            self.previous_states = previous_states
        else:
            self.previous_states = []

    @property
    def incomplete(self):
        """Is the dot at the end of the rule. """
        return self.dot_position < len(self.rule.rhs)

    @property
    def next_category(self):
        if self.incomplete:
            return self.rule.rhs[self.dot_position]
        else:
            return ''

    def __repr__(self):
        return '{} -> {}.{}, [{}, {}]'.format(self.rule.lhs,
                                              ' '.join(self.rule.rhs[:self.dot_position]),
                                              ' '.join(self.rule.rhs[self.dot_position:]),
                                              self.span_start,
                                              self.span_stop)

class ChartIndexError(IndexError):
    pass

class Chart:
    def __init__(self, sentence):
        self.sentence = sentence
        self._chart = [self._create_queue() for _ in range(len(sentence) + 1)]

    def enqueue(self, state, position):
        self._chart[position].append(state)

    def _create_queue(self):
        return []

    def __getitem__(self, index):
        try:
          return self._chart[index]
        except IndexError:
            raise ChartIndexError('Index out of range.')

    def __len__(self):
        return len(self._chart)

    def __iter__(self):
        return iter(self._chart)

class Parser:
    def __init__(self, grammar):
        self._grammar = grammar

    def _grammar_rules_for(self, lhs):
        for rule in self._grammar:
            if lhs == rule.lhs:
                yield rule

    def _predict(self, state, chart):
        # Check that state is not complete.
        for rule in self._grammar_rules_for(state.next_category):
            if not rule.preterminal:
                chart.enqueue(State(rule=rule,
                                    span_start=state.span_stop,
                                    span_stop=state.span_stop,
                                    dot_position=0),
                              state.span_stop)

    def _is_applicable_preterminal(self, rule, state, chart):
        return (rule.lhs == state.next_category and
                ''.join(rule.rhs) == chart.sentence[state.span_stop] and
                rule.preterminal)

    def _scan(self, state, chart):
        # TODO Check that state is not complete.
        for rule in self._grammar:
            if self._is_applicable_preterminal(rule, state, chart):
                chart.enqueue(
                    State(rule=rule,
                          span_start=state.span_stop,
                          span_stop=state.span_stop + 1,
                          dot_position=1),
                    state.span_stop + 1
                )

    def _complete(self, state, chart):
        """Given a completed state, looks for all rules in the grammar 'waiting' for that state to get completed."""
        # Check that state is complete.
        for candidate_state in chart[state.span_start]:
            if (candidate_state.next_category == state.rule.lhs) and (candidate_state.span_stop == state.span_start):
                chart.enqueue(
                    State(
                        rule=candidate_state.rule,
                        span_start=candidate_state.span_start,
                        span_stop=state.span_stop,
                        dot_position=candidate_state.dot_position + 1,
                        previous_states=candidate_state.previous_states + [state]
                    ),
                    state.span_stop
                )

    def _tree_from_parse(self, state):
        if state.rule.preterminal:
            return [state.rule.lhs, ''.join(state.rule.rhs)]
        tree = []
        tree.append(state.rule.lhs)
        for contributor in sorted(state.previous_states, key=lambda s: s.span_start):
            tree.append(self._tree_from_parse(contributor))
        return tree

    def _full_parses(self, chart):
        parses = []
        for state in chart[len(chart) - 1]:
            if not state.incomplete and state.rule.lhs == 'GAMMA':
                parses.append(state)
        return parses

    def parse(self, words):
        chart = Chart(words)
        chart.enqueue(
            State(
                rule=Rule('GAMMA', ['S']),
                span_start=0,
                span_stop=0,
                dot_position=0
            ),
            0
        )
        for i in range(len(words) + 1):
            for state in chart[i]:
                if state.incomplete:
                    self._predict(state, chart)
                    self._scan(state, chart)
                else:
                    self._complete(state, chart)

        return [self._tree_from_parse(p) for p in self._full_parses(chart)]

def main():
    # Maybe replace "preterminal" with "lexicon"?
    GRAMMAR = [
        Rule('S', ['VP']),
        Rule('VP', ['V', 'NP']),
        Rule('NP', ['Det', 'Nominal']),
        Rule('Det', ['that'], preterminal=True),
        Rule('Nominal', ['flight'], preterminal=True),
        Rule('V', ['Book'], preterminal=True)
    ]

    words = ['Book', 'that', 'flight']
    parser = Parser(GRAMMAR)
    print(parser.parse(words))



if __name__ == '__main__':
    main()