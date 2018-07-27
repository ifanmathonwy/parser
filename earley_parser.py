"""A library implementing the Earley parser.

The Earley parser parses strings from a given context-free language.

Example usage:
  from parser.earley_parser import EarleyParser
  from parser.grammar import Grammar, Rule

  grammar = Grammar(
      Rule('S', ['VP']),
      Rule('VP', ['V', 'NP']),
      Rule('NP', ['Det', 'Nominal']),
      Rule('Det', ['that'], preterminal=True),
      Rule('Nominal', ['flight'], preterminal=True),
      Rule('V', ['Book'], preterminal=True)
  )

  my_parser = EarleyParser(grammar)

  words = ['Book', 'that', 'flight']

  parses = my_parser.parse(words)

This implementation is based on the description of the algorithm given in
'Speech and Language Processing, 2nd Edition' by D. Jurafsky and
J. H. Martin (2009).
"""

from grammar import Rule

_GAMMA = '_GAMMA'


class State:
    """A state in the Earley chart."""

    def __init__(self, rule, span_start, span_stop, dot_position, previous_states=None):
        """Initializer for the State class.

        Args:
            rule (Rule): A rule whose progress in the parse is being tracked
                by the State.
            span_start (int): The beginning of the input span for which the
                constituent predicted by the State should apply.
            span_stop (int): The end index of the input span for which the
                constituent predicted by the State should apply.
            dot_position (int): The index representing the progress through
                the constituent predicted by the State. It indexes interstices,
                starting from 0.
            previous_states (list<State>): A list of States which allowed the
                progress through the current State to advance.
        """
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
        """Has the dot not reached the end of the rule?"""
        return self.dot_position < len(self.rule.rhs)

    @property
    def next_category(self):
        """What is the category after the dot?"""
        if self.incomplete:
            return self.rule.rhs[self.dot_position]
        else:
            return ''

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (self.rule == other.rule and
                self.span_start == other.span_start and
                self.span_stop == other.span_stop and
                self.dot_position == other.dot_position and
                self.previous_states == other.previous_states)

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        # TODO change to proper repr when done debugging.
        return '{} -> {} . {}, [{}, {}]'.format(self.rule.lhs,
                                                ' '.join(self.rule.rhs[:self.dot_position]),
                                                ' '.join(self.rule.rhs[self.dot_position:]),
                                                self.span_start,
                                                self.span_stop)


class EarleyChartIndexError(IndexError):
    pass


class EarleyChart:
    """Details full and partial Earley parses for a sequence of words and a grammar."""

    def __init__(self, sentence):
        """Initializer for the EarleyChart class.

        Args:
            sentence (list<string>): A list of words representing the object
                to be parsed.
        """
        self.sentence = sentence
        self._chart = [self._create_queue() for _ in range(len(sentence) + 1)]

    def enqueue(self, state, position):
        """Add a state to the given position in the EarleyChart."""
        if state not in self._chart[position]:
            self._chart[position].append(state)

    def _create_queue(self):
        return []

    def __getitem__(self, index):
        try:
            return self._chart[index]
        except IndexError:
            raise EarleyChartIndexError('Index out of range.')

    def __len__(self):
        return len(self._chart)

    def __iter__(self):
        return iter(self._chart)


class EarleyAlgorithm:
    """The Earley algorithm."""

    def __init__(self, grammar):
        """Initializer for the EarleyAlgorithm class.

        Args:
            grammar (Grammar): The Grammar to be used to parse inputs.
        """
        self._grammar = grammar

    def _grammar_rules_for(self, lhs):
        for rule in self._grammar:
            if lhs == rule.lhs:
                yield rule

    def _predict(self, state, chart):
        for rule in self._grammar_rules_for(state.next_category):
            if not rule.preterminal:
                chart.enqueue(State(rule=rule,
                                    span_start=state.span_stop,
                                    span_stop=state.span_stop,
                                    dot_position=0),
                              state.span_stop)

    def _is_applicable_preterminal(self, rule, state, chart):
        if state.span_stop >= len(chart.sentence):
            return False
        return (rule.preterminal and rule.lhs == state.next_category and
                ''.join(rule.rhs) == chart.sentence[state.span_stop])

    def _scan(self, state, chart):
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
        """Given completed state, updates all rules in the grammar awaiting its completion."""
        for candidate_state in chart[state.span_start]:
            if ((candidate_state.next_category == state.rule.lhs) and
                    (candidate_state.span_stop == state.span_start)):
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
            if not state.incomplete and state.rule.lhs == _GAMMA:
                parses.append(state)
        return parses

    def parse(self, words):
        """Parses a sequence of words.

        Args:
            words (list<string>): The sequence of words to be parsed.

        Returns:
            A list of parse trees valid for the given input sequence, or [] if
                no valid parse.
        """
        chart = EarleyChart(words)
        chart.enqueue(
            State(
                rule=Rule(_GAMMA, [self._grammar.distinguished_symbol]),
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

        return [self._tree_from_parse(p)[1] for p in self._full_parses(chart)]


class EarleyParser:
    """An Earley parser."""

    def __init__(self, grammar):
        """Initializer for the EarleyParser class.

        Args:
            grammar (Grammar): The Grammar to be used to parse inputs.
        """
        self._algorithm = EarleyAlgorithm(grammar)

    def parse(self, words):
        """Parses a sequence of words.

        TODO: Choose output format here? GraphViz? Tree library?

        Args:
            words (list<string>): The sequence of words to be parsed.

        Returns:
            A list of parse trees valid for the given input sequence, or [] if
                no valid parse.
        """
        return self._algorithm.parse(words)
