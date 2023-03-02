"""
COMS W4705 - Natural Language Processing - Spring 2023
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
from math import fsum, isclose


class Pcfg(object):
    """
    Represent a probabilistic context free grammar.
    """

    def __init__(self, grammar_file):
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None
        self.read_rules(grammar_file)

    def read_rules(self, grammar_file):
        for line in grammar_file:
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line:
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else:
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()

    def parse_rule(self, rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";", 1)
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False.
        """
        # TODO, Part 1
        for nonterminal in self.lhs_to_rules:
            rules = self.lhs_to_rules[nonterminal]
            prob_sum = fsum([rule[2] for rule in rules])
            if not isclose(prob_sum, 1.0):
                print(f"Sum of probabilities for {nonterminal} is {prob_sum}")
                return False
            for rule in rules:
                if len(rule[1]) == 1 and rule[1][0] in self.lhs_to_rules:
                    print(f"Rule {rule} has a nonterminal on the right hand side.")
                    # print(f"Rule {rule} has a terminal on the right hand side.")
                    return False
                if len(rule[1]) == 2 and (
                    rule[1][0] not in self.lhs_to_rules
                    or rule[1][1] not in self.lhs_to_rules
                ):
                    print(f"Rule {rule} has a terminal on the right hand side.")
                    return False
                if len(rule[1]) > 2:
                    print(
                        f"Rule {rule} has more than two symbols on the right hand side."
                    )
                    return False
        if self.startsymbol not in self.lhs_to_rules:
            print(f"Start symbol {self.startsymbol} is not in the grammar.")
            return False
        return True


if __name__ == "__main__":
    # with open(sys.argv[1], "r") as grammar_file:
    with open("atis3.pcfg", "r") as grammar_file:
        grammar = Pcfg(grammar_file)
        print(grammar.verify_grammar())
