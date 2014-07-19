import sys
sys.dont_write_bytecode = True
import os
import ast
import json
from textsearch import TextSearch

#loads
def load_test():
    y = []
    for a in open('test_data.txt', 'rb'):
        y.append(a)
    y = y[0]
    return ast.literal_eval(y)

#tests
def test_search():
    test_data = load_test()
    t = TextSearch(test_data, True)
    return t

t = test_search()
