"""Grammars and rules."""

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