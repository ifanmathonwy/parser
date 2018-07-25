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


GRAMMAR = [
    Rule('S', ['VP']),
    Rule('VP', ['V', 'NP']),
    Rule('NP', ['Det', 'Nominal']),
    Rule('Det', ['that'], preterminal=True),
    Rule('Nominal', ['flight'], preterminal=True),
    Rule('V', ['Book'], preterminal=True)
]

def grammar_rules_for(lhs, grammar):
    for rule in grammar:
        if lhs == rule.lhs:
            yield rule

def predict(state, chart):
    # Check that state is not complete.
    for rule in grammar_rules_for(state.next_category, GRAMMAR):
        if not rule.preterminal:
            chart.enqueue(State(rule=rule,
                                span_start=state.span_stop,
                                span_stop=state.span_stop,
                                dot_position=0),
                          state.span_stop)

def is_applicable_preterminal(rule, state, chart):
    return (rule.lhs == state.next_category and
            ''.join(rule.rhs) == chart.sentence[state.span_stop] and
            rule.preterminal)

def scan(state, chart):
    # Check that state is not complete.
    for rule in GRAMMAR:
        if is_applicable_preterminal(rule, state, chart):
            chart.enqueue(
                State(rule=rule,
                      span_start=state.span_stop,
                      span_stop=state.span_stop + 1,
                      dot_position=1),
                state.span_stop + 1
            )

def complete(state, chart):
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


def trace(state):
    print(state)
    for previous_state in state.previous_states:
        trace(previous_state)
    # Figure out a function for returning a parse tree object using this trace.

def full_parses(chart):
    parses = []
    for state in chart[len(chart)-1]:
        if not state.incomplete and state.rule.lhs == 'GAMMA':
            parses.append(state)

    for parse in parses:
        print('****************************')
        trace(parse)
        print('****************************')


def parse(words, grammar):
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
                predict(state, chart)
                scan(state, chart)
            else:
                complete(state, chart)
    full_parses(chart)


def test_complete():
    chart = Chart(['Book', 'these', 'flights'])
    state = State(rule=Rule('V', ['Book']), span_start=0, span_stop=1, dot_position=1)
    chart[0].append(
        State(Rule('VP', ['V', 'NP']), 0, 0, 0)
    )
    complete(state, chart)
    print(chart._chart)


def test_predict():
    chart = Chart(['Book', 'these', 'flights'])
    state = State(Rule('S', ['VP']), span_start=0, span_stop=0, dot_position=0)
    predict(state, chart)
    print(chart._chart)

def test_scan():
    chart = Chart(['Book', 'these', 'flights'])
    state = State(Rule('VP', ['V', 'NP'], preterminal=True), span_start=0, span_stop=0, dot_position=0)
    scan(state, chart)
    print(chart._chart)


def main():
    words = ['Book', 'that', 'flight']
    parse(words, GRAMMAR)
    # chart = Chart(['Book', 'these', 'flights'])
    # print(len(chart))
    # print(chart._chart)
    # assert(chart[0] is not chart[1])
    # r = Rule('S', ['NP', 'VP'])
    # print(r)
    # s = State(rule=r,
    #           span_start=0,
    #           span_stop=0,
    #           dot_position=0)
    # print(s)
    # test_predict()
    # test_scan()
    # test_complete()


if __name__ == '__main__':
    main()