# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Event in calendar."""

import persistent
import zope.app.container.contained
import zope.interface

import zeit.cms.content.util

import zeit.calendar.interfaces


class Event(persistent.Persistent,
            zope.app.container.contained.Contained):

    zope.interface.implements(zeit.calendar.interfaces.ICalendarEvent)

    added_by = None
    completed = False
    description = None
    location = None
    related = ()
    ressort = None
    start = None
    thema = False
    title = None
