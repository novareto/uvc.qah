import doctest
import uvc.qah
import re
import six
import os
import unittest
import zope.app.wsgi.testlayer
import zope.testbrowser.wsgi

from pkg_resources import resource_listdir
from zope.app.wsgi.testlayer import http
from zope.testing import renormalizing


class Layer(
        zope.testbrowser.wsgi.TestBrowserLayer,
        zope.app.wsgi.testlayer.BrowserLayer):
    pass

layer = Layer(uvc.qah, allowTearDown=True)


checker = renormalizing.RENormalizing([
    # Accommodate to exception wrapping in newer versions of mechanize
    (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
    ])


def http_call(app, method, path, data=None, handle_errors=False, **kw):
    """Function to help make RESTful calls.

    method - HTTP method to use
    path - testbrowser style path
    data - (body) data to submit
    kw - any request parameters
    """

    if path.startswith('http://localhost'):
        path = path[len('http://localhost'):]
    request_string = '%s %s HTTP/1.1\n' % (method, path)
    for key, value in kw.items():
        request_string += '%s: %s\n' % (key, value)
    if data is not None:
        request_string += '\r\n'
        request_string += data

    if six.PY3:
        request_string = request_string.encode()

    result = http(app, request_string, handle_errors=handle_errors)
    return result


def suiteFromPackage(name):
    layer_dir = 'functional'
    files = resource_listdir(__name__, '{}/{}'.format(layer_dir, name))
    suite = unittest.TestSuite()
    globs = dict(
        getRootFolder=layer.getRootFolder,
        http_call=http_call,
        wsgi_app=layer.make_wsgi_app)
    optionflags = (
        doctest.ELLIPSIS +
        doctest.NORMALIZE_WHITESPACE +
        doctest.REPORT_NDIFF +
        renormalizing.IGNORE_EXCEPTION_MODULE_IN_PYTHON2)
    for filename in files:
        if filename == '__init__.py':
            continue

        test = None
        if filename.endswith('.py'):
            dottedname = 'uvc.qah.tests.%s.%s.%s' % (
                layer_dir, name, filename[:-3])
            test = doctest.DocTestSuite(
                dottedname,
                checker=checker,
                extraglobs=globs,
                optionflags=optionflags)
        elif filename.endswith('.txt'):
            test = doctest.DocFileSuite(
                os.path.join(layer_dir, name, filename),
                optionflags=optionflags,
                globs=globs)
        if test is not None:
            test.layer = layer
            suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['adhoc']:
        suite.addTest(suiteFromPackage(name))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
