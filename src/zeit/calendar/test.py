# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import os
import unittest

from zope.testing import doctest

import zope.app.testing.functional

import zeit.cms.testing
import zeit.calendar.calendar


CalendarLayer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'CalendarLayer', allow_teardown=True)


optionflags = (doctest.ELLIPSIS |
               doctest.INTERPRET_FOOTNOTES |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_NDIFF)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(
        zeit.calendar.calendar,
        optionflags=optionflags))
    suite.addTest(doctest.DocFileSuite(
        'README.txt',
        optionflags=optionflags))
    suite.addTest(zeit.cms.testing.FunctionalDocFileSuite(
        'calendar.txt',
        layer=CalendarLayer))
    return suite
