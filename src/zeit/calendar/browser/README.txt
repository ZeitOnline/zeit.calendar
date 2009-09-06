=====================
Calendar Browser Test
=====================

The calendar is rendered as a table showing one full month at a time.

Create a browser first:

>>> from z3c.etestbrowser.testing import ExtendedTestBrowser 
>>> browser = ExtendedTestBrowser()
>>> browser.addHeader('Authorization', 'Basic user:userpw')
>>> browser.addHeader('Accept-Language', 'en')


Calendar
========

The calendar is registered as a utility ICalendar and is reachable via
`/calendar`. By default it shows the current month. Firgure out what the
current month is:

>>> import datetime
>>> now = datetime.datetime.now()

Open the calendar and check for the current month:

>>> browser.open('http://localhost/++skin++cms/calendar/month.html')
>>> '%s/%s' % (now.month, now.year) in browser.contents
True
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE ...
    <title> calendar – Events for ... </title>
    ...
    <table id="calendar" class="month">
      <thead>
        <tr>
          <th>Mon</th>
          <th>Tue</th>
          <th>Wed</th>
          <th>Thu</th>
          <th>Fri</th>
          <th>Sat</th>
          <th>Sun</th>
       </tr>
      </thead>
...


Events
======

Events can be added to the calendar:

>>> browser.open('http://localhost/++skin++cms/calendar/'
...              '@@zeit.calendar.Event.AddForm')


When we just open the add form, the start date is empty:

>>> browser.getControl(name='form.start').value
''

Aborting takes us back to the calendar:

>>> browser.getControl('Cancel').click()
>>> print browser.title.strip()
calendar – Events for ...

Create an entry:

>>> browser.open('http://localhost/++skin++cms/calendar/'
...              '@@zeit.calendar.Event.AddForm')

>>> browser.getControl(name='form.start').value = '2006-05-04'
>>> browser.getControl(name='form.end').value = '2006-05-03'
>>> browser.getControl(name='form.title').value = 'Bild erstellen'
>>> browser.getControl(name='form.description').value = '... fuer Artikel'
>>> browser.getControl('Add Related content').click()
>>> browser.getControl(name='form.related.0.').value = (
...     'http://xml.zeit.de/online')
>>> browser.getControl(name='form.actions.add').click()

We've set the end date before the start date. This won't work of couse:

>>> print browser.contents
<?xml ...
    <div id="messages" class="haveMessages">
      <ul>
        <li class="error">The event ends before it starts.</li>
      </ul>
      ...


Remove the end date again:

>>> browser.getControl(name='form.end').value = ''
>>> browser.getControl(name='form.actions.add').click()

After successful adding, the calendar is displayed for the added month:
    
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE ...
  <td class="day">
    <div class="day" id="calendarday4">
      4
      <a href="http://.../calendar/@@zeit.calendar.Event.AddForm?form.start=2006-05-04"
         class="add-event" title="Add event">
        <img alt="(+)"
             src="http://localhost/++skin++cms/@@/zeit.cms/icons/insert.png" />
      </a>
      <script ...
        ...</script>
    </div>
      <div class="event misc">
        <a title="Complete event"
           class="event-not-completed"
           href="http://localhost/++skin++cms/calendar/bild-erstellen/@@complete">
          <input type="checkbox" />
        </a>
      <a ...Bild erstellen </a>...
    </div>
  </td>
... 


The event can be edited again:

>>> browser.getLink('Bild erstellen').click()

There is no ressort set currently:

>>> browser.getControl('Ressort').displayValue
['(no value)']
>>> browser.getControl('Ressort').displayOptions
['(no value)', 'Deutschland', 'International', ...]

The inital prioirty is not set:

>>> browser.getControl('Priority').displayValue
['(no value)']
>>> browser.getControl('Priority').displayOptions
['(no value)', '^^ mandatory', '^ important', '> suggestion']


On the edit screen there is also information about who created the image:

>>> print browser.contents
<?xml ...
          <span>Added by</span>
        </label>
        ...
        <div class="widget">User</div>
        ...

Add a related and set the ressort:

>>> browser.getControl(name='form.related.0.').value
'http://xml.zeit.de/online'
>>> browser.getControl(name='form.related.0.').value = (
...     'http://xml.zeit.de/online/2007')
>>> browser.getControl('Ressort').displayValue = ['International']
>>> browser.getControl('Apply').click()

After editing we're also back at the calendar view.

>>> bookmark = browser.url

Drag and drop support
+++++++++++++++++++++

The calendar has DnD support: Documents can be dropped on it which yields the
add form which an already assigned document. Construct the url manually here:

>>> url = ("http://localhost/++skin++cms/calendar/"
...        "@@zeit.calendar.Event.AddForm?form.start=2006-05-04"
...        "&form.related.count=1"
...        "&form.related.0.=http://xml.zeit.de/politik.feed")
>>> browser.open(url)
>>> browser.getControl(name="form.related.0.").value
'http://xml.zeit.de/politik.feed'

Navigating
==========

There are 5 navigation links in the calendar. We have added an event for
2006-05-04, so we are looking at the page for May 2006. After clicking the "one
year back" link, we're at 2005/05:

>>> browser.open(bookmark)
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 5/2006'
>>> browser.getLink("«").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 5/2005'

The "month back" link takes us to 4/2005 then:
    
>>> browser.getLink("‹").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 4/2005'

When we go one month back from 1/2005 we reach 12/2004:

>>> browser.getLink("‹").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 3/2005'
>>> browser.getLink("‹").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 2/2005'
>>> browser.getLink("‹").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 1/2005'
>>> browser.getLink("‹").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 12/2004'


The "month forward" again will result in 1/2005:

>>> browser.getLink("›").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 1/2005'


The "year forward" leaps us to 1/2006:
    
>>> browser.getLink("»").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 1/2006'

When we freshly enter the calendar we'll still see 1/2006:

>>> browser.getLink("Calendar").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 1/2006'


Week Overview
=============

There is also an overview showing yesterday and the next 7 days. We were
looking at 1/2006, so we see the week starting at 31.12.2005:

>>> browser.getLink('Week').click()
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE ...
  <table id="calendar" class="week">
    <thead>
      <tr>
              <th>Sat, 31. Dec</th>
              <th>Sun, 1. Jan</th>
              <th>Mon, 2. Jan</th>
              <th>Tue, 3. Jan</th>
              <th>Wed, 4. Jan</th>
              <th>Thu, 5. Jan</th>
              <th>Fri, 6. Jan</th>
              <th>Sat, 7. Jan</th>
      </tr>
    </thead>
    ...

>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 31.12.2005 - 07.01.2006'

Navigation works like with the month calendar. Move one day forward:
    
>>> browser.getLink("›").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 01.01.2006 - 08.01.2006'

Move 7 days forward:
    
>>> browser.getLink("»").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 08.01.2006 - 15.01.2006'

Move 1 day backward:
    
>>> browser.getLink("‹").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 07.01.2006 - 14.01.2006'

Move 7 days backward:

>>> browser.getLink("«").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 31.12.2005 - 07.01.2006'

Finally, the "today" link points us to the current week:

>>> browser.getLink("Today").click()
>>> browser.getLink("Month").click()
>>> '%s/%s' % (now.month, now.year) in browser.contents
True


Next week's overview
====================

Next week's overview is similar to the week overview except that it starts on
the next Monday and ends on the Sunday following that. Since we saw that
2006/1/2 was a Monday, next week's overview ranges from 2006/1/2 through
2006/1/8 for both 2005/12/30 and 2005/12/31:

>>> browser.open(
...     'http://localhost/++skin++cms/calendar/month.html'
...     '?year:int=2005&month:int=12&day:int=30')
>>> browser.getLink('Next week').click()
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE ...
  <table id="calendar" class="week">
    <thead>
      <tr>
              <th>Mon, 2. Jan</th>
              <th>Tue, 3. Jan</th>
              <th>Wed, 4. Jan</th>
              <th>Thu, 5. Jan</th>
              <th>Fri, 6. Jan</th>
              <th>Sat, 7. Jan</th>
              <th>Sun, 8. Jan</th>
      </tr>
    </thead>
    ...

>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 02.01.2006 - 08.01.2006'

>>> browser.open(
...     'http://localhost/++skin++cms/calendar/month.html'
...     '?year:int=2005&month:int=12&day:int=31')
>>> browser.getLink('Next week').click()
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE ...
  <table id="calendar" class="week">
    <thead>
      <tr>
              <th>Mon, 2. Jan</th>
              <th>Tue, 3. Jan</th>
              <th>Wed, 4. Jan</th>
              <th>Thu, 5. Jan</th>
              <th>Fri, 6. Jan</th>
              <th>Sat, 7. Jan</th>
              <th>Sun, 8. Jan</th>
      </tr>
    </thead>
    ...

>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 02.01.2006 - 08.01.2006'


Next four weeks
===============

The overview of the next four weeks has features of both the month calendar
and next week's overview: it starts on the Monday following the selected date
and covers exactly 28 days. The layout of the calendar is similar to that of
the month view:

>>> browser.getLink('Next four weeks').click()
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE ...
    <title> calendar – Events for 02.01.2006 - 29.01.2006 </title>
    ...
    <table id="calendar" class="month">
      <thead>
        <tr>
          <th>Mon</th>
          <th>Tue</th>
          <th>Wed</th>
          <th>Thu</th>
          <th>Fri</th>
          <th>Sat</th>
          <th>Sun</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td class="day">
            <div class="day" id="calendarday2">
              2
              <a ...
        </tr>
        ...
        <tr>
              ...?form.start=2006-01-29', 'calendarday29');</script>
            </div>
          </td>
        </tr>
      </tbody>
...

>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 02.01.2006 - 29.01.2006'

Navigating forward and backward moves us by one week, fast forward and fast
backwards by four:

>>> browser.getLink("‹").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 26.12.2005 - 22.01.2006'

>>> browser.getLink("»").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 23.01.2006 - 19.02.2006'

>>> browser.getLink("›").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 30.01.2006 - 26.02.2006'

>>> browser.getLink("«").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 02.01.2006 - 29.01.2006'


Day view
========

The overview of the selected day's events looks like the week overview except
that it covers only one day:

>>> browser.open(
...     'http://localhost/++skin++cms/calendar/month.html'
...     '?year:int=2005&month:int=12&day:int=31')
>>> browser.getLink('Day').click()
>>> print browser.contents
<?xml version="1.0"?>
<!DOCTYPE ...
    <title> calendar – Events for 31.12.2005 </title>
    ...
    <table id="calendar" class="week">
      <thead>
        <tr>
          <th>Sat, 31. Dec</th>
        </tr>
      </thead>
    ...

>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 31.12.2005'

Navigating forward and backward moves us by one day, fast forward and fast
backwards by one week:

>>> browser.getLink("‹").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 30.12.2005'

>>> browser.getLink("»").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 06.01.2006'

>>> browser.getLink("›").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 07.01.2006'

>>> browser.getLink("«").click()
>>> browser.etree.xpath('//div[@id="content"]//h1')[0].text
'Events for 31.12.2005'


Deleting Events
===============

Open a page with an event in:

>>> browser.open(
...     'http://localhost/++skin++cms/calendar/month.html'
...     '?year:int=2006&month:int=5')
>>> '5/2006' in browser.contents
True
>>> 'Bild erstellen' in browser.contents
True

Open the event:

>>> browser.getLink('Bild erstellen').click()

On the edit page there is a delete control:

>>> browser.getControl("Delete").click()
>>> print browser.contents
<?xml ...
        <li class="message">Event deleted.</li>
        ...
>>> '5/2006' in browser.contents
True
>>> 'Bild erstellen' in browser.contents
False


Filtering events
================

Events can be filtered for their ressort. Initially all events are shown.

>>> browser.getLink('Calendar').click()
>>> print browser.contents
<?xml ...
    <div id="ressort-filter">
      <form>
        <div class="ressort">
          <label class="politik">
            <input type="checkbox" value="1"
                   checked="checked" name="politik" />
            <span>Politik</span>
          </label>
        </div>
        <div class="ressort">
          <label class="wirtschaft">
            <input type="checkbox" value="1"
                   checked="checked" name="wirtschaft" />
            <span>Wirtschaft</span>
          </label>
        </div>
        <div class="ressort">
          <label class="kultur">
            <input type="checkbox" value="1"
                   checked="checked" name="kultur" />
            <span>Kultur</span>
          </label>
        </div>
        <div class="ressort">
          <label class="misc">
            <input type="checkbox" value="1"
                   checked="checked" name="misc" />
            <span>weitere Themen</span>
          </label>
        </div>
      </form>
    </div>
    ...

Indivdual events are also marked with a css class when they have a ressort
associated:

>>> browser.open('http://localhost/++skin++cms/calendar/'
...              '@@zeit.calendar.Event.AddForm')
>>> browser.getControl('Start').value = '2008-08-07'
>>> browser.getControl('Title').value = 'Olympia'
>>> browser.getControl('Ressort').displayValue = ['International']
>>> browser.getControl(name='form.actions.add').click()

>>> browser.open('http://localhost/++skin++cms/calendar/'
...              '@@zeit.calendar.Event.AddForm')
>>> browser.getControl('Start').value = '2008-08-07'
>>> browser.getControl('Title').value = 'Oelpreis'
>>> browser.getControl('Ressort').displayValue = ['Wirtschaft']
>>> browser.getControl(name='form.actions.add').click()

>>> print browser.contents
<?xml ...
      <div class="event wirtschaft">
        ...
        <a href="http://localhost/++skin++cms/calendar/oelpreis"
            ...Oelpreis </a>...
      </div>
      <div class="event politik">
        ...
        <a href="http://localhost/++skin++cms/calendar/olympia"
            ...Olympia </a>...
      </div>
      ...


When we hide "Politik" this is indicated by the "hidden" css class. Hiding is
done in the browser via Javascript. The current hiding state is transferred to
the server via an AJAX call so the server can restore the state later.
Construct a request to the server to hide politik:

>>> browser.open('http://localhost/++skin++cms/calendar/'
...              '@@hide-ressort?ressort=politik')

Accessing the calendar now shows 1. that the Politk checkbox is not checked and
2. that the politk event is hidden:

>>> browser.open('http://localhost/++skin++cms/calendar')
>>> print browser.contents
<?xml ...
    <div id="ressort-filter">
      <form>
        <div class="ressort">
          <label class="politik">
            <input type="checkbox" value="1" name="politik" />
            <span>Politik</span>
          </label>
        </div>
        <div class="ressort">
          <label class="wirtschaft">
            <input type="checkbox" value="1"
                   checked="checked" name="wirtschaft" />
            <span>Wirtschaft</span>
          </label>
        </div>
        <div class="ressort">
          <label class="kultur">
            <input type="checkbox" value="1"
                   checked="checked" name="kultur" />
            <span>Kultur</span>
          </label>
        </div>
        <div class="ressort">
          <label class="misc">
            <input type="checkbox" value="1"
                   checked="checked" name="misc" />
            <span>weitere Themen</span>
          </label>
        </div>
      </form>
    </div>
    ...
      <div class="event wirtschaft">
        ...
        <a href="http://localhost/++skin++cms/calendar/oelpreis"
            ...Oelpreis </a>...
      </div>
      <div class="event politik hidden">
        ...
        <a href="http://localhost/++skin++cms/calendar/olympia"
            ...Olympia </a>...
      </div>
      ...


We can of course hide more than one at a time:

>>> browser.open('http://localhost/++skin++cms/calendar/'
...              '@@hide-ressort?ressort=wirtschaft')
>>> browser.open('http://localhost/++skin++cms/calendar')
>>> print browser.contents
<?xml ...
    <div id="ressort-filter">
      <form>
        <div class="ressort">
          <label class="politik">
            <input type="checkbox" value="1" name="politik" />
            <span>Politik</span>
          </label>
        </div>
        <div class="ressort">
          <label class="wirtschaft">
            <input type="checkbox" value="1" name="wirtschaft" />
            <span>Wirtschaft</span>
          </label>
        </div>
        <div class="ressort">
          <label class="kultur">
            <input type="checkbox" value="1"
                   checked="checked" name="kultur" />
            <span>Kultur</span>
          </label>
        </div>
        <div class="ressort">
          <label class="misc">
            <input type="checkbox" value="1"
                   checked="checked" name="misc" />
            <span>weitere Themen</span>
          </label>
        </div>
      </form>
    </div>
    ...
      <div class="event wirtschaft hidden">
        ...
        <a href="http://localhost/++skin++cms/calendar/oelpreis"
            ...Oelpreis </a>...
      </div>
      <div class="event politik hidden">
        ...
        <a href="http://localhost/++skin++cms/calendar/olympia"
            ...Olympia </a>...
      </div>
      ...


Let's show politik again:

>>> browser.open('http://localhost/++skin++cms/calendar/'
...              '@@show-ressort?ressort=politik')
>>> browser.open('http://localhost/++skin++cms/calendar')
>>> print browser.contents
<?xml ...
    <div id="ressort-filter">
      <form>
        <div class="ressort">
          <label class="politik">
            <input type="checkbox" value="1"
                   checked="checked" name="politik" />
            <span>Politik</span>
          </label>
        </div>
        <div class="ressort">
          <label class="wirtschaft">
            <input type="checkbox" value="1" name="wirtschaft" />
            <span>Wirtschaft</span>
          </label>
        </div>
        <div class="ressort">
          <label class="kultur">
            <input type="checkbox" value="1"
                   checked="checked" name="kultur" />
            <span>Kultur</span>
          </label>
        </div>
        <div class="ressort">
          <label class="misc">
            <input type="checkbox" value="1"
                   checked="checked" name="misc" />
            <span>weitere Themen</span>
          </label>
        </div>
      </form>
    </div>
    ...
      <div class="event wirtschaft hidden">
        ...
        <a href="http://localhost/++skin++cms/calendar/oelpreis"
            ...Oelpreis </a>...
      </div>
      <div class="event politik">
        ...
        <a href="http://localhost/++skin++cms/calendar/olympia"
            ...Olympia </a>...
      </div>
      ...


When we add an event to no ressort it will be added to the misc class:

>>> browser.open('http://localhost/++skin++cms/calendar/'
...              '@@zeit.calendar.Event.AddForm')
>>> browser.getControl('Start').value = '2008-08-07'
>>> browser.getControl('Title').value = 'Ocht'
>>> browser.getControl(name='form.actions.add').click()
>>> print browser.contents
<?xml ...
      <div class="event misc">
        ...
        <a href="http://localhost/++skin++cms/calendar/ocht"
            ...Ocht </a>...
      </div>
      ...


Other ressors are also added to misc:

>>> browser.getLink('Ocht').click()
>>> browser.getControl('Ressort').displayValue = ['Computer']
>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml ...
      <div class="event misc">
        ...
        <a href="http://localhost/++skin++cms/calendar/ocht"
            ...Ocht </a>...
      </div>
      ...


Those can be hidden as well:

>>> browser.open('http://localhost/++skin++cms/calendar/'
...              '@@hide-ressort?ressort=misc')
>>> browser.open('http://localhost/++skin++cms/calendar')
>>> print browser.contents
<?xml ...
      <div class="event misc hidden">
        ...
        <a href="http://localhost/++skin++cms/calendar/ocht"
            ...Ocht </a>...
      </div>
      ...


Completing events
=================

Events are completed by clicking on the checkbox in the calendar. The checkbox
is not checked thus the event is not completed:

>>> print browser.contents
<?xml...
      <div class="event politik">
        <a title="Complete event"
           class="event-not-completed"
           href="http://localhost/++skin++cms/calendar/olympia/@@complete">
          <input type="checkbox" />
        </a>
        <a href="http://localhost/++skin++cms/calendar/olympia"
            ...Olympia </a>...
      </div>
      ...

Click the complete link (the link is hard to select in the testbrowser, so just
open it):

>>> browser.open('http://localhost/++skin++cms/calendar/olympia/@@complete')
>>> print browser.contents
<?xml...
        <li class="message">Event completed.</li>
        ...
      <div class="event completed politik">
        <a title="Reactivate event"
           class="event-completed"
           href="http://localhost/++skin++cms/calendar/olympia/@@uncomplete">
          <input type="checkbox" checked="checked" />
        </a>
        <a href="http://localhost/++skin++cms/calendar/olympia"
            ...Olympia </a>...
      </div>
      ...

We can of course also "uncomplete" the event:

>>> browser.open('http://localhost/++skin++cms/calendar/olympia/@@uncomplete')
>>> print browser.contents
<?xml...
        <li class="message">Event reactivated.</li>
        ...
      <div class="event politik">
        <a title="Complete event"
           class="event-not-completed"
           href="http://localhost/++skin++cms/calendar/olympia/@@complete">
          <input type="checkbox" />
        </a>
        <a href="http://localhost/++skin++cms/calendar/olympia"
            ...Olympia </a>...
      </div>
      ...

Priority
========

The priority is visible in the calendar. The olympia article as no priority
set:

>>> browser.open('http://localhost/++skin++cms/calendar')
>>> print browser.contents
<?xml...
      <div class="event politik">
        <a title="Complete event"
           class="event-not-completed"
           href="http://localhost/++skin++cms/calendar/olympia/@@complete">
          <input type="checkbox" />
        </a>
        <a href="http://localhost/++skin++cms/calendar/olympia"...>
          <span class="priority"></span>
          Olympia
        </a>...
      </div>
      ...

Set to "suggestion"

>>> browser.getLink('Olympia').click()
>>> browser.getControl('Priority').displayValue = ['suggestion']
>>> browser.getControl('Apply').click()
>>> print browser.contents
<?xml...
      <div class="event politik">
        <a title="Complete event"
           class="event-not-completed"
           href="http://localhost/++skin++cms/calendar/olympia/@@complete">
          <input type="checkbox" />
        </a>
        <a href="http://localhost/++skin++cms/calendar/olympia"...>
          <span class="priority">&gt; suggestion</span>
          Olympia
        </a>...
      </div>
      ...


Tooltips
========

There are tooltips which are displayed via javascript. Each event gets an id
(which is unique)[#unique]_:

>>> browser.open('http://localhost/++skin++cms/calendar')
>>> print browser.contents
<?xml...
      <div class="event...">
        ...
        <a href="http://localhost/++skin++cms/calendar/olympia"...id="event...">
          ...Olympia
        </a>...
        <script language="javascript">
          new zeit.cms.LinkToolTip('event...');
          </script>
          ...


The LinkToolTip opens the @@drag-pane.html view:


>>> browser.open(
...     'http://localhost/++skin++cms/calendar/olympia/@@drag-pane.html')
>>> print browser.contents
  <div class="calendar-drag-title">Olympia</div>
  <div class="calendar-drag-description"></div>



Link in the sidebar
===================

In the vivi skin there is a link in the sidebar:

>>> browser.open('/++skin++vivi')
>>> print browser.contents
<...
   <div id="sidebar" class="sidebar-expanded"><div class="panel" id="sidebar-calendar">
   <a href="http://localhost/++skin++vivi/calendar">Calendar</a>...

>>> browser.getLink('Calendar').click()
>>> print browser.title.strip()
calendar – Events for ...


.. [#unique] We explicitly test this since there was a bug where the ids where
    not unique.

    >>> browser.open('http://localhost/++skin++cms/calendar')
    >>> nodes = browser.etree.xpath("//div[contains(@class, 'event')]/a[@id]")
    >>> ids = [node.get('id') for node in nodes]
    >>> len(ids)
    3
    >>> len(set(ids))
    3
