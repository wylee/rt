import doctest

from . import data, response


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(data))
    tests.addTests(doctest.DocTestSuite(response))
    return tests


