# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

from zope.testing import doctest
import unittest
import zeit.calendar.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        'event.txt',
        optionflags=zeit.calendar.testing.optionflags))
    suite.addTest(zeit.calendar.testing.FunctionalDocFileSuite(
        'README.txt',
        'calendar_view.txt',
        ))
    return suite
