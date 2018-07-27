"""Grammars and rules."""

import re


class Rule:
    """A rule in a context-free grammar."""

    def __init__(self, lhs, rhs, preterminal=False, probability=1.0):
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
        self.probability = probability

    def __repr__(self):
        # TODO change to proper repr when done debugging.
        return '{} -> {}'.format(self.lhs, ' '.join(self.rhs))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (self.lhs == other.lhs and
                self.rhs == other.rhs and
                self.preterminal == other.preterminal)

    def __ne__(self, other):
        return not self.__class__.__eq__(self, other)

class Grammar:
    """A container for Rules with methods to construct from various sources.

    TODO: Initialize from BNF.
    TODO: Initialize from arrow format.
    TODO: Abstract away terminal/preterminal distinction by providing lexicon/POS method.
    """

    def __init__(self, *rules, distinguished_symbol='S'):
        self._grammar = []
        self._distinguished_symbol = distinguished_symbol
        for rule in rules:
            self._grammar.append(rule)

    def add_rule(self, rule):
        self._grammar.append(rule)

    @classmethod
    def from_csv(cls, path):
        raise NotImplementedError('Creating a Grammar from CSV is not yet implemented.')

    def __iter__(self):
        return iter(self._grammar)

    def __contains__(self, item):
        return item in self._grammar

    def __len__(self):
        return len(self._grammar)

    @property
    def distinguished_symbol(self):
        return self._distinguished_symbol

class Regex:
    "A regex which can function as a matcher for a rhs preterminal label."

    def __init__(self, regex):
        self._regex = re.compile(regex)

    def __eq__(self, other):
        if self._regex.match(other):
            return True
        return False

    def __ne__(self, other):
        return not self.__class__.__eq__(self, other)