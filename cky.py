"""
COMS W4705 - Natural Language Processing - Spring 2023
Homework 2 - Parsing with Probabilistic Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg


### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.
    """
    if not isinstance(table, dict):
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table:
        if (
            not isinstance(split, tuple)
            and len(split) == 2
            and isinstance(split[0], int)
            and isinstance(split[1], int)
        ):
            sys.stderr.write(
                "Keys of the backpointer table must be tuples (i,j) representing spans.\n"
            )
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write(
                "Value of backpointer table (for each span) is not a dict.\n"
            )
            return False
        for nt in table[split]:
            if not isinstance(nt, str):
                sys.stderr.write(
                    "Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n"
                )
                return False
            bps = table[split][nt]
            if isinstance(bps, str):  # Leaf nodes may be strings
                continue
            if not isinstance(bps, tuple):
                sys.stderr.write(
                    "Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(
                        bps
                    )
                )
                return False
            if len(bps) != 2:
                sys.stderr.write(
                    "Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(
                        bps
                    )
                )
                return False
            for bp in bps:
                if not isinstance(bp, tuple) or len(bp) != 3:
                    sys.stderr.write(
                        "Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(
                            bp
                        )
                    )
                    return False
                if not (
                    isinstance(bp[0], str)
                    and isinstance(bp[1], int)
                    and isinstance(bp[2], int)
                ):
                    print(bp)
                    sys.stderr.write(
                        "Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(
                            bp
                        )
                    )
                    return False
    return True


def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.
    """
    if not isinstance(table, dict):
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table:
        if (
            not isinstance(split, tuple)
            and len(split) == 2
            and isinstance(split[0], int)
            and isinstance(split[1], int)
        ):
            sys.stderr.write(
                "Keys of the probability must be tuples (i,j) representing spans.\n"
            )
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write(
                "Value of probability table (for each span) is not a dict.\n"
            )
            return False
        for nt in table[split]:
            if not isinstance(nt, str):
                sys.stderr.write(
                    "Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n"
                )
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write(
                    "Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(
                        prob
                    )
                )
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True


class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar):
        """
        Initialize a new parser instance from a grammar.
        """
        self.grammar = grammar

    def is_in_language(self, tokens):
        """
        Membership checking. Parse the input tokens and return True if
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        n = len(tokens)
        chart = [[[] for _ in range(n + 1)] for _ in range(n + 1)]
        for i in range(n):
            for rules in self.grammar.rhs_to_rules[(tokens[i],)]:
                chart[i][i + 1].append(rules[0])

        for l in range(2, n + 1):
            for i in range(n - l + 1):
                j = i + l
                for k in range(i + 1, j):
                    for rhs, rules in self.grammar.rhs_to_rules.items():
                        if (
                            len(rhs) == 2
                            and rhs[0] in chart[i][k]
                            and rhs[1] in chart[k][j]
                        ):
                            chart[i][j].extend([rule[0] for rule in rules])
                            chart[i][j] = list(set(chart[i][j]))
        return self.grammar.startsymbol in chart[0][n]

    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
        # TODO, part 3
        n = len(tokens)
        table = {(i // (n + 1), i % (n + 1)): dict() for i in range((n + 1) ** 2)}
        probs = {(i // (n + 1), i % (n + 1)): dict() for i in range((n + 1) ** 2)}
        for i in range(n):
            for rule in self.grammar.rhs_to_rules[(tokens[i],)]:
                table[(i, i + 1)][rule[0]] = rule[1][0]
                probs[(i, i + 1)][rule[0]] = math.log(rule[2])

        for l in range(2, n + 1):
            for i in range(n - l + 1):
                j = i + l
                for k in range(i + 1, j):
                    for rhs, rules in self.grammar.rhs_to_rules.items():
                        if (
                            len(rhs) == 2
                            and rhs[0] in table[(i, k)]
                            and rhs[1] in table[(k, j)]
                        ):
                            if i == 1 and j == 5 and k == 3:
                                for rule in rules:
                                    print(rule)
                            for rule in rules:
                                lhs = rule[0]
                                prob = (
                                    probs[(i, k)][rhs[0]]
                                    + probs[(k, j)][rhs[1]]
                                    + rule[2]
                                )
                                if (
                                    lhs not in table[(i, j)]
                                    or prob > probs[(i, j)][lhs]
                                ):
                                    table[(i, j)][lhs] = (
                                        (rhs[0], i, k),
                                        (rhs[1], k, j),
                                    )
                                    probs[(i, j)][lhs] = prob
        return table, probs


def get_tree(chart, i, j, nt):
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4
    if i + 1 == j:
        return (nt, chart[(i, j)][nt])
    else:
        lnt, i, k = chart[(i, j)][nt][0]
        rnt, _, j = chart[(i, j)][nt][1]
        return (
            nt,
            get_tree(chart, i, k, lnt),
            get_tree(chart, k, j, rnt),
        )


if __name__ == "__main__":
    with open("atis3.pcfg", "r") as grammar_file:
        grammar = Pcfg(grammar_file)
        parser = CkyParser(grammar)
        toks = ["flights", "from", "miami", "to", "cleveland", "."]
        print(parser.is_in_language(toks))
        table, probs = parser.parse_with_backpointers(toks)
        print("====\n\n\n\n", get_tree(table, 0, len(toks), grammar.startsymbol))
        assert check_table_format(table)
        assert check_probs_format(probs)
