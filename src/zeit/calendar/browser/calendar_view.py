# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Calendar views."""

import calendar
import datetime
import persistent
import time
import zope.annotation
import zope.app.container.contained
import zope.app.form.browser.interfaces
import zope.cachedescriptors.property
import zope.component
import zope.i18n.format
import zope.interface
import zope.security.interfaces
import zope.session.interfaces
import zope.viewlet.viewlet

import zeit.calendar.browser.interfaces
import zeit.calendar.calendar
import zeit.calendar.interfaces
import zeit.cms.browser.menu
import zeit.cms.browser.view
from zeit.calendar.i18n import MessageFactory as _


one_day = datetime.timedelta(days=1)
one_week = datetime.timedelta(days=7)


class MenuItem(zeit.cms.browser.menu.GlobalMenuItem):

    title = _("Calendar")
    viewURL = 'calendar'
    pathitem = 'calendar'


class IndexRedirect(zeit.cms.browser.view.Base):

    def __call__(self):
        last_view = zeit.calendar.browser.interfaces.ILastView(
            self.request.principal).last_view
        self.redirect('%s?%s' % (self.url(last_view),
                                 self.request.get('QUERY_STRING')))
        return ''


class CalendarBase(object):

    misc_class = 'misc'
    combined_ressort = (
        dict(title=u'Politik',
             ressorts=('Deutschland', 'International'),
             css_class='politik'),
        dict(title=u'Wirtschaft',
             ressorts=('Wirtschaft', 'Finanzen'),
             css_class='wirtschaft'),
        dict(title=u'Kultur',
             ressorts=('Kultur', 'Feuilleton', 'Musik', 'Literatur'),
             css_class='kultur'),
        dict(title=u'weitere Themen',
             css_class=misc_class))

    ressort_css = {}
    for combined in combined_ressort:
        for ressort in combined.get('ressorts', []):
            ressort_css[ressort] = combined['css_class']

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.today = datetime.date.today()

    def update(self):
        self._delete_event()
        self._register_last_view()

        # Store potential request values to session:
        self.selected_day, self.selected_month, self.selected_year

    @zope.cachedescriptors.property.Lazy
    def selected_date(self):
        return datetime.date(self.selected_year,
                             self.selected_month,
                             self.selected_day)

    @zope.cachedescriptors.property.Lazy
    def selected_day(self):
        return self._get_request_or_session_value('day', self.today.day)

    @zope.cachedescriptors.property.Lazy
    def selected_month(self):
        return self._get_request_or_session_value('month', self.today.month)

    @zope.cachedescriptors.property.Lazy
    def selected_year(self):
        return self._get_request_or_session_value('year', self.today.year)

    def _get_request_or_session_value(self, name, default):
        value = self.request.get(name)
        if value:
            self.session[name] = value
        else:
            value = self.session.get(name, default)
        return value

    @zope.cachedescriptors.property.Lazy
    def url(self):
        return zope.component.getMultiAdapter(
            (self, self.request),
            name='absolute_url')()

    def get_navigation_url(self, date):
        return '%s?%s' % (self.url, self.get_navigation_query(date))

    def get_navigation_query(self, date):
        return 'year:int=%d&month:int=%d&day:int=%d' % (
            date.year, date.month, date.day)

    def _get_day_dict(self, date):
        events = self.context.getEvents(date)
        event_dicts = None
        if events:
            events = sorted(events, key=lambda e: e.priority, reverse=True)
            events = sorted(events, key=lambda e: e.completed)
            event_dicts = [dict(obj=event,
                                priority=self.get_event_priority(event),
                                id='event.%f' % time.time(),
                                css=self.get_event_css(event))
                            for event in events]
        return {'day': date.day,
                'date_str': '%4d-%02d-%02d' % (date.year, date.month,
                                               date.day),
                'have_events': self.context.haveEvents(date),
                'events': event_dicts,
                'is_today': date == self.today}

    def _register_last_view(self):
        zeit.calendar.browser.interfaces.ILastView(
            self.request.principal).last_view = self.__name__

    def _delete_event(self):
        delete_id = self.request.get('delete_event')
        if delete_id is None:
            return
        del self.context[delete_id]

    def get_event_css(self, event):
        classes = ['event']
        if event.completed:
            classes.append('completed')
        if event.thema:
            classes.append('thema')
        ressort_class = self.ressort_css.get(event.ressort, self.misc_class)
        classes.append(ressort_class)
        if ressort_class in self.hidden_ressorts:
            classes.append('hidden')
        return ' '.join(classes)

    def get_event_priority(self, event):
        source = zeit.calendar.interfaces.ICalendarEvent['priority'].source
        terms = zope.component.queryMultiAdapter(
            (source, self.request),
            zope.app.form.browser.interfaces.ITerms)
        if terms is None:
            return ''
        try:
            term = terms.getTerm(event.priority)
        except KeyError:
            return ''
        return term.title

    @zope.cachedescriptors.property.Lazy
    def session(self):
        return zope.session.interfaces.ISession(self.request)['zeit.calendar']

    @zope.cachedescriptors.property.Lazy
    def hidden_ressorts(self):
        last_view = zeit.calendar.browser.interfaces.ILastView(
            self.request.principal, None)
        if last_view is None:
            return ()
        return last_view.hidden_ressorts


class Day(CalendarBase):

    @zope.cachedescriptors.property.Lazy
    def title(self):
        return _('Events for ${date}', mapping=dict(
            date='%02d.%02d.%4d' % (self.selected_day, self.selected_month,
                                    self.selected_year)))

    @zope.cachedescriptors.property.Lazy
    def selected_week_calendar(self):
        return [self._get_day_dict(self.selected_date)]

    @zope.cachedescriptors.property.Lazy
    def day_names(self):
        formatter = self.request.locale.dates.getFormatter('date')
        pattern = u'EEE, d. MMM'
        return [formatter.format(self.selected_date, pattern)]

    @zope.cachedescriptors.property.Lazy
    def forward(self):
        return self.selected_date + one_day

    @zope.cachedescriptors.property.Lazy
    def backward(self):
        return self.selected_date - one_day

    @zope.cachedescriptors.property.Lazy
    def fastforward(self):
        return self.selected_date + one_week

    @zope.cachedescriptors.property.Lazy
    def fastbackward(self):
        return self.selected_date - one_week


class Calendar(CalendarBase):

    @zope.cachedescriptors.property.Lazy
    def title(self):
        return _('Events for ${month}/${year}',
                 mapping=dict(month=self.selected_month,
                              year=self.selected_year))

    @zope.cachedescriptors.property.Lazy
    def selected_month_calendar(self):
        year = self.selected_year
        month = self.selected_month
        cal = calendar.monthcalendar(year, month)
        result = []

        for week_list in cal:
            week = []
            result.append(week)
            for day_no in week_list:
                if day_no:
                    date = datetime.date(year, month, day_no)
                    day = self._get_day_dict(date)
                else:
                    day = None
                week.append(day)

        return result

    @property
    def day_names(self):
        return self.request.locale.dates.calendars[
            'gregorian'].getDayAbbreviations()

    @zope.cachedescriptors.property.Lazy
    def forward(self):
        month = self.selected_month + 1
        year = self.selected_year
        if month > 12:
            month = 1
            year += 1
        return datetime.date(year, month, 1)

    @zope.cachedescriptors.property.Lazy
    def backward(self):
        month = self.selected_month - 1
        year = self.selected_year
        if month < 1:
            month = 12
            year -= 1
        return datetime.date(year, month, 1)

    @zope.cachedescriptors.property.Lazy
    def fastforward(self):
        month = self.selected_month
        year = self.selected_year + 1
        return datetime.date(year, month, 1)

    @zope.cachedescriptors.property.Lazy
    def fastbackward(self):
        month = self.selected_month
        year = self.selected_year -1
        return datetime.date(year, month, 1)


class Week(CalendarBase):

    @zope.cachedescriptors.property.Lazy
    def title(self):
        start = self.start_date
        end = self.end_date
        # XXX we could/should use a locale dependent date formatter here
        return _('Events for ${start} - ${end}',
                 mapping=dict(
                     start='%02d.%02d.%4d' % (start.day, start.month,
                                              start.year),
                     end='%02d.%02d.%4d' % (end.day, end.month, end.year)))

    @zope.cachedescriptors.property.Lazy
    def day_names(self):
        formatter = self.request.locale.dates.getFormatter('date')
        pattern = u'EEE, d. MMM'
        return [formatter.format(day, pattern) for day in self.day_list]

    @zope.cachedescriptors.property.Lazy
    def selected_week_calendar(self):
        return [self._get_day_dict(day) for day in self.day_list]

    @zope.cachedescriptors.property.Lazy
    def start_date(self):
        return self.selected_date - one_day

    @zope.cachedescriptors.property.Lazy
    def end_date(self):
        return self.start_date + one_week

    @zope.cachedescriptors.property.Lazy
    def day_list(self):
        return list(zeit.calendar.calendar.date_range(self.start_date,
                                                      self.end_date))

    @zope.cachedescriptors.property.Lazy
    def forward(self):
        return self.selected_date + one_day

    @zope.cachedescriptors.property.Lazy
    def backward(self):
        return self.selected_date - one_day

    @zope.cachedescriptors.property.Lazy
    def fastforward(self):
        return self.selected_date + one_week

    @zope.cachedescriptors.property.Lazy
    def fastbackward(self):
        return self.selected_date - one_week


class NextWeek(Week):

    @zope.cachedescriptors.property.Lazy
    def start_date(self):
        return (self.selected_date - one_day*self.selected_date.weekday()
                + one_week)

    @zope.cachedescriptors.property.Lazy
    def end_date(self):
        return self.start_date - one_day + one_week


class NextFourWeeks(NextWeek):

    @zope.cachedescriptors.property.Lazy
    def selected_month_calendar(self):
        result = []
        start = self.start_date

        for week_no in xrange(4):
            result.append(
                [self._get_day_dict(date) for date in
                 zeit.calendar.calendar.date_range(start, start + 6*one_day)])
            start += one_week

        return result

    @property
    def day_names(self):
        return self.request.locale.dates.calendars[
            'gregorian'].getDayAbbreviations()

    @zope.cachedescriptors.property.Lazy
    def end_date(self):
        return self.start_date - one_day + 4*one_week

    @zope.cachedescriptors.property.Lazy
    def forward(self):
        return self.selected_date + one_week

    @zope.cachedescriptors.property.Lazy
    def backward(self):
        return self.selected_date - one_week

    @zope.cachedescriptors.property.Lazy
    def fastforward(self):
        return self.selected_date + 4*one_week

    @zope.cachedescriptors.property.Lazy
    def fastbackward(self):
        return self.selected_date - 4*one_week


class Sidebar(zope.viewlet.viewlet.ViewletBase):
    """Calendar sidebar view."""

    @zope.cachedescriptors.property.Lazy
    def calendar(self):
        return zope.component.getUtility(zeit.calendar.interfaces.ICalendar)


class LastView(persistent.Persistent,
               zope.app.container.contained.Contained):

    zope.interface.implements(zeit.calendar.browser.interfaces.ILastView)
    zope.component.adapts(zope.security.interfaces.IPrincipal)

    last_view = 'month.html'
    hidden_ressorts = frozenset()


lastViewFactory = zope.annotation.factory(LastView)


class HideRessort(object):
    """Hide a ressort."""

    def __call__(self, ressort):
        last_view = zeit.calendar.browser.interfaces.ILastView(
            self.request.principal)
        last_view.hidden_ressorts = last_view.hidden_ressorts.union([ressort])


class ShowRessort(object):
    """Show a ressort."""

    def __call__(self, ressort):
        last_view = zeit.calendar.browser.interfaces.ILastView(
            self.request.principal)
        last_view.hidden_ressorts = last_view.hidden_ressorts.difference(
            [ressort])
