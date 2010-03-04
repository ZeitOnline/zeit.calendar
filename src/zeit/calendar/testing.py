# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import os
import pkg_resources
import zeit.cms.testing
import zope.app.testing.functional


product_config = {
    'zeit.calendar': {
        'ressortgroup-url': 'file://%s' % pkg_resources.resource_filename(
            'zeit.calendar.tests.fixtures', 'ressortgroups.xml'),
        }
    }


layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'CalendarLayer', allow_teardown=True)


optionflags = (doctest.ELLIPSIS |
               doctest.INTERPRET_FOOTNOTES |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_NDIFF)


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', layer)
    kw.setdefault('product_config', product_config)
    kw['package'] = zope.testing.doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):
    layer = layer
    product_config = product_config
