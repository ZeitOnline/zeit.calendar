from zeit.cms.browser.resources import Resource, Library
import zeit.cms.browser.resources


lib = Library('zeit.calendar', 'resources')
Resource('calendar.css')
Resource('calendar.js', depends=[zeit.cms.browser.resources.base])
