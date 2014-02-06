# Copyright (c) 2014 gocept gmbh & co. kg
# See also LICENSE.txt

from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.calendar', 'resources')
Resource('calendar.css')
Resource('calendar.js', depends=[zeit.cms.browser.resources.base])
