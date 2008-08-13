========
Calendar
========

Events
======

Events are objects which can be added to the calendar. Let's create an event:

>>> import datetime
>>> import zope.interface.verify
>>> import zeit.calendar.interfaces
>>> from zeit.calendar.event import Event
>>> event = Event()
>>> event.start=datetime.date(2007, 6, 5)
>>> event.title = u"Fotogalerie erstellen"
>>> event.description = u"FG fuer Foo erstellen."
>>> event
<zeit.calendar.event.Event object at 0x...>
>>> zope.interface.verify.verifyObject(
...     zeit.calendar.interfaces.ICalendarEvent, event)
True
>>> event.start
datetime.date(2007, 6, 5)
>>> event.title
u'Fotogalerie erstellen'
>>> event.description
u'FG fuer Foo erstellen.'
>>> event.completed
False


Calendar
========

The calendar is a container for events. Create a calendar. Initally it's empty:

>>> import zeit.calendar.calendar
>>> calendar = zeit.calendar.calendar.Calendar()
>>> calendar
<zeit.calendar.calendar.Calendar object at 0x...>
>>> zope.interface.verify.verifyObject(
...     zeit.calendar.interfaces.ICalendar, calendar)
True
>>> len(calendar)
0



Add the event to the calendar:

>>> calendar['bla'] = event
>>> len(calendar)
1


We can get the event by date using the getEvents method:

>>> date = datetime.date(2007, 6, 5)
>>> events = list(calendar.getEvents(date))
>>> events
[<zeit.calendar.event.Event object at 0x...>]
>>> events[0].title
u'Fotogalerie erstellen'
>>> calendar.haveEvents(date)
True


On other dates there are no events:

>>> list(calendar.getEvents(datetime.date(2006, 6, 5)))
[]
>>> calendar.haveEvents(datetime.date(2006, 6, 5))
False
>>> list(calendar.getEvents(datetime.date(2007, 6, 6)))
[]
>>> list(calendar.getEvents(datetime.date(2007, 5, 6)))
[]


After removing the event from the calendar, it's also gone from getEvents:

>>> del calendar['bla']
>>> list(calendar.getEvents(date))
[]
>>> calendar.haveEvents(date)
False


Changing Calendar Events
========================

When chaning events the calendar index is updated automatically via a
subscriber to `ObjectModifiedEvent`.  So we add the event again:

>>> calendar['ev'] = event
>>> events = list(calendar.getEvents(datetime.date(2007, 6, 5)))
>>> events
[<zeit.calendar.event.Event object at 0x...>]

We change the start of the event. The index is not updated, yet:

>>> event.start = datetime.date(2008, 10, 21)
>>> list(calendar.getEvents(datetime.date(2007, 6, 5)))
[<zeit.calendar.event.Event object at 0x...>]
>>> list(calendar.getEvents(datetime.date(2008, 10, 21)))
[]

After updating the index, getEvent returns the result correctly again:

>>> from zeit.calendar.calendar import updateIndexOnEventChange
>>> updateIndexOnEventChange(event, object())
>>> list(calendar.getEvents(datetime.date(2007, 6, 5)))
[]
>>> list(calendar.getEvents(datetime.date(2008, 10, 21)))
[<zeit.calendar.event.Event object at 0x...>]


Events spanning multiple days
=============================

When we set the end date of an event to a day after the start date, the event
will be listed for each day from start through end:

>>> event.end = datetime.date(2008, 10, 23)
>>> updateIndexOnEventChange(event, object())
>>> list(calendar.getEvents(datetime.date(2008, 10, 21)))
[<zeit.calendar.event.Event object at 0x...>]
>>> list(calendar.getEvents(datetime.date(2008, 10, 22)))
[<zeit.calendar.event.Event object at 0x...>]
>>> list(calendar.getEvents(datetime.date(2008, 10, 23)))
[<zeit.calendar.event.Event object at 0x...>]
>>> list(calendar.getEvents(datetime.date(2008, 10, 24)))
[]

When we delete the event from the calendar, it is removed neatly from all
these days:

>>> del calendar['ev']
>>> list(calendar.getEvents(datetime.date(2008, 10, 21)))
[]
>>> list(calendar.getEvents(datetime.date(2008, 10, 22)))
[]
>>> list(calendar.getEvents(datetime.date(2008, 10, 23)))
[]
