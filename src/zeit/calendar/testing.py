# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import pkg_resources
import zeit.cms.testing
import doctest


product_config = """
<product-config zeit.calendar>
    ressortgroup-url file://%s
</product-config>
""" % (
    pkg_resources.resource_filename(
        'zeit.calendar.tests.fixtures', 'ressortgroups.xml'),)


layer = zeit.cms.testing.ZCMLLayer(
    'ftesting.zcml',
    product_config=zeit.cms.testing.cms_product_config + product_config)


def FunctionalDocFileSuite(*args, **kw):
    kw.setdefault('layer', layer)
    kw['package'] = doctest._normalize_module(kw.get('package'))
    return zeit.cms.testing.FunctionalDocFileSuite(*args, **kw)


class FunctionalTestCase(zeit.cms.testing.FunctionalTestCase):

    layer = layer
