import doctest

from . import data


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(data))
    return tests


