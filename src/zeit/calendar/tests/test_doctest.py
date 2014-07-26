# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import doctest
import unittest
import zeit.calendar.calendar
import zeit.calendar.testing
import zeit.cms.testing


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(
        zeit.calendar.calendar,
        optionflags=zeit.cms.testing.optionflags))
    suite.addTest(doctest.DocFileSuite(
        'README.txt',
        package='zeit.calendar',
        optionflags=zeit.cms.testing.optionflags))
    suite.addTest(zeit.calendar.testing.FunctionalDocFileSuite(
        'calendar.txt',
        package='zeit.calendar',
    ))
    return suite
