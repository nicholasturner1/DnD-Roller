#!/usr/bin/env python3

import re
import random
import string
import operator


DIE_TYPE_REGEXP = re.compile("d[0-9]+")
DIE_MULT_REGEXP = re.compile("[0-9]*d")


def main():

    while True:
        line = input("What would you like to roll?\n")
        if all(map(lambda x: x in string.whitespace, line)):
            break
        result = ParseTree(line)
        print("{expr} = {res}\n".format(expr=result, res=result.value))        


class ParseTree(object):

    def __init__(self, fields_or_str):

        if isinstance(fields_or_str, str):
            fields = self.parse_fields(fields_or_str)
        elif isinstance(fields_or_str, list):
            assert all(list(map(lambda x: isinstance(x,str), fields_or_str)))
            fields = fields_or_str
        else:
            raise Exception("improper argument to ParseTree")

        self.root_node = self.parse_node(fields, self.find_root_node(fields))
        self.value = self.root_node.value

    def parse_fields(self, fields_string):
        """
        Splits a string into a list of string fields, each describing a set of
        die rolls or a static value
        """
        fields = []
        curr = ""
        for c in fields_string:
            if c == "+":
                assert len(fields) > 0 or curr != ""
                fields.append(curr.strip())
                curr = ""
                fields.append("+")
            elif c == "-":
                assert len(fields) > 0 or curr != ""
                if curr == "" and fields[-1] == "-":
                    #negative number
                    continue
                else:
                    fields.append(curr.strip())
                    curr = ""
                    fields.append("-")
            else:
                curr += c

        if curr != "":
            fields.append(curr.strip())

        return fields

    def find_root_node(self, fields):
        if "+" in fields:
            return fields.index("+")
        elif "-" in fields:
            return len(fields) - 1 - list(reversed(fields)).index("-")
        else:
            assert len(fields) == 1, "No op fields w/ multiple values"
            return 0

    def parse_node(self, fields, root_index):

        root_field = fields[root_index]

        if root_field == "+":
            assert root_index != 0
            assert root_index != len(fields)

            return OpNode(ParseTree(fields[:root_index]),
                          ParseTree(fields[(root_index+1):]),
                          operator.add)

        elif root_field == "-":
            assert root_index != 0
            assert root_index != len(fields)

            return OpNode(ParseTree(fields[:root_index]),
                          ParseTree(fields[(root_index+1):]),
                          operator.sub)

        elif is_multi_die(root_field):
            multiplier = get_multiplier(root_field)
            return ParseTree(self.multi_expression(root_field, multiplier))

        else:
            return ValueNode(fields[root_index])

    def multi_expression(self, field, mult):
        """Splits a multi die roll into multiple single die rolls"""
        fields = [self.make_single_roll(field)] * mult
        result = [fields[0]]

        for i in range(1,len(fields)):
            result.append("+")
            result.append(fields[i])

        return result

    def make_single_roll(self, field):
        """Turns any die roll into a single roll"""
        die_type = get_die_type(field)
        return "1d{}".format(die_type)

    def __repr__(self):
        return "ParseTree<{}>".format(repr(self.root_node))

    def __str__(self):
        return str(self.root_node)


class OpNode(object):
    """
    Node in the tree representing an arithmetic operation
    Only + and - for now
    """

    def __init__(self, left, right, op):
        self.left = left
        self.right = right
        self.op = op

        self.value = op(left.value, right.value)

    def __repr__(self):
        if self.op == operator.add:
            opstring = "+"
        elif self.op == operator.sub:
            opstring = "-"
        else:
            raise Exception("unknown operator in OpNode")

        return "OpNode<{left} {op} {right}>".format(left=repr(self.left),
                                                    op=opstring,
                                                    right=repr(self.right))

    def __str__(self):
        if self.op == operator.add:
            opstring = "+"
        elif self.op == operator.sub:
            opstring = "-"
        else:
            raise Exception("unknown operator in OpNode")

        return "{left} {op} {right}".format(left=str(self.left),
                                            op=opstring,
                                            right=str(self.right))


class ValueNode(object):
    """Node in the tree representing a single die roll or a single number"""

    def __init__(self, field):
        assert isinstance(field, str)

        self.field = field
        self.isdie = "d" in field

        if self.isdie:
            self.max_value = get_die_type(field)
            self.value = random.randint(1,self.max_value)
        else:
            self.max_value = None
            self.value = int(field)

    def __repr__(self):
        if self.isdie:
            return "ValueNode<{},d{}>".format(self.value, self.max_value)
        else:
            return "ValueNode<{}>".format(self.value)

    def __str__(self):
        if self.isdie and self.value == self.max_value:
            return "!*{}*!(d{})".format(self.value, self.max_value)
        elif self.isdie:
            return "{}(d{})".format(self.value, self.max_value)
        else:
            return "{}".format(self.value, self.max_value)


#====================================================
#Helper fns

def get_multiplier(field):
    """Extracts a die multiplier from a field if it's a die"""
    match = DIE_MULT_REGEXP.match(field)

    if match:
        matchstr = match.group(0)
        if len(matchstr) == 1: #only the 'd'
            return 1
        else:
            return int(match.group(0)[:-1])
    else:
        return 1


def is_multi_die(field):
    """Tests whether a field is a die roll with multiplier higher than 1"""
    return get_multiplier(field) > 1


def get_die_type(field=None):
    """Extracts the die type from a die string"""

    if field is None:
        field = self.field

    match = DIE_TYPE_REGEXP.search(field)

    if match:
        return int(match.group(0)[1:])
    else:
        raise Exception("doesn't look like a die to me")


if __name__ == "__main__":
    main()
