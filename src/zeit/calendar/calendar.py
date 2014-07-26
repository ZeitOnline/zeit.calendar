# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime

import BTrees.OOBTree

import zope.component
import zope.interface
import zope.lifecycleevent
import zope.proxy

import zope.app.container.btree

import zeit.calendar.interfaces


class Calendar(zope.app.container.btree.BTreeContainer):

    zope.interface.implements(zeit.calendar.interfaces.ICalendar)

    def __init__(self):
        super(Calendar, self).__init__()
        self._date_index = BTrees.OOBTree.OOBTree()
        self._key_index = BTrees.OOBTree.OOBTree()

    def getEvents(self, date):
        """Return the events occuring on `date`."""
        for event_id in self._date_index.get(date, []):
            yield self[event_id]

    def haveEvents(self, date):
        """Return whether there are events occuring on `date`."""
        return bool(self._date_index.get(date))

    def __setitem__(self, key, value):
        event = zeit.calendar.interfaces.ICalendarEvent(value)
        super(Calendar, self).__setitem__(key, value)
        self._index(key, event.start, event.end)

    def __delitem__(self, key):
        super(Calendar, self).__delitem__(key)
        self._unindex(key)

    def _index(self, key, start, end):
        if end is None:
            check = (start,)
        else:
            check = (start, end)
        for day in check:
            if not isinstance(day, datetime.date):
                raise ValueError("Expected date object, got %r instead" % day)
        for day in date_range(start, end):
            try:
                day_idx = self._date_index[day]
            except KeyError:
                self._date_index[day] = day_idx = BTrees.OOBTree.OOTreeSet()
            day_idx.insert(key)
        self._key_index[key] = (start, end)

    def _unindex(self, key):
        start, end = self._key_index[key]
        del self._key_index[key]
        for day in date_range(start, end):
            self._date_index[day].remove(key)


@zope.component.adapter(
    zeit.calendar.interfaces.ICalendarEvent,
    zope.lifecycleevent.IObjectModifiedEvent)
def updateIndexOnEventChange(calendar_event, event):
    calendar = zope.proxy.removeAllProxies(calendar_event.__parent__)
    key = calendar_event.__name__
    calendar._unindex(key)
    calendar._index(key, calendar_event.start, calendar_event.end)


def date_range(start, end):
    """Generate all datetime.date objects from start through end.

    If end is None or earlier than start, yield only start. The range is never
    empty so every event is always listed for at least one day. Otherwise
    faulty dates might render an event unreachable via the index.

    >>> day1 = datetime.date(2008, 1, 30)
    >>> day2 = datetime.date(2008, 2, 2)

    >>> list(date_range(day1, day2))
    [datetime.date(2008, 1, 30), datetime.date(2008, 1, 31),
     datetime.date(2008, 2, 1), datetime.date(2008, 2, 2)]
    >>> list(date_range(day1, None))
    [datetime.date(2008, 1, 30)]
    >>> list(date_range(day1, day1))
    [datetime.date(2008, 1, 30)]
    >>> list(date_range(day2, day1))
    [datetime.date(2008, 2, 2)]

    """
    if end is None or end <= start:
        yield start
    else:
        for i in xrange(start.toordinal(), end.toordinal() + 1):
            yield datetime.date.fromordinal(i)
