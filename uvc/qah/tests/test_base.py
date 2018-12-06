import doctest
import re
import os
import unittest

from pkg_resources import resource_listdir
from zope.testing import cleanup, renormalizing


def cleanUpZope(test):
    cleanup.cleanUp()


checker = renormalizing.RENormalizing([
    # str(Exception) has changed from Python 2.4 to 2.5 (due to
    # Exception now being a new-style class).  This changes the way
    # exceptions appear in traceback printouts.
    (re.compile(
        r"ConfigurationExecutionError: <class '([\w.]+)'>:"),
        r'ConfigurationExecutionError: \1:')])


def suiteFromPackage(name):
    layer_dir = 'base'
    files = resource_listdir(__name__, '{}/{}'.format(layer_dir, name))
    suite = unittest.TestSuite()

    optionflags = (
        doctest.ELLIPSIS +
        doctest.NORMALIZE_WHITESPACE +
        doctest.REPORT_NDIFF +
        renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2)

    for filename in files:
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        test = None
        if filename.endswith('.py'):
            dottedname = 'uvc.qah.tests.%s.%s.%s' % (
                layer_dir, name, filename[:-3])
            test = doctest.DocTestSuite(
                dottedname,
                checker=checker,
                optionflags=optionflags)
        elif filename.endswith('.txt'):
            test = doctest.DocFileSuite(
                os.path.join(layer_dir, name, filename),
                optionflags=optionflags)
        if test is not None:
            suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['token']:  # ADD !
        suite.addTest(suiteFromPackage(name))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
