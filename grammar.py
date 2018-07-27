"""Grammars and rules.

TODO: Disallow GAMMA in user-defined rules.
"""

class Rule:
    """A rule in a context-free grammar."""

    def __init__(self, lhs, rhs, preterminal=False):
        """Initializer for the Rule class.

        Args:
            lhs (string): The label for the left-hand side of the production
                rule.
            rhs (list<string>): The labels of the children of the production
                rule.
            preterminal (bool): Does this production bottom-out at a single
                terminal, i.e. a lexicon entry?
        """
        self.lhs = lhs
        self.rhs = rhs
        self.preterminal = preterminal

    def __repr__(self):
        # TODO change to proper repr when done debugging.
        return '{} -> {}'.format(self.lhs, ' '.join(self.rhs))

class Grammar:
    """A container for Rules with methods to construct from various sources.

    TODO: Initialize from BNF.
    TODO: Initialize from arrow format.
    TODO: Abstract away terminal/preterminal distinction by providing lexicon/POS method.
    """

    def __init__(self):
        self._grammar = []

    def add_rule(self, rule):
        self._grammar.append(rule)

    @classmethod
    def from_csv(cls, path):
        raise NotImplementedError('Creating a Grammar from CSV is not yet implemented.')

    def __iter__(self):
        return iter(self._grammar)

    def __contains__(self, item):
        return item in self._grammar