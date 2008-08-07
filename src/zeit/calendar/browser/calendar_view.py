# Copyright (c) 2007-2008 gocept gmbh & co. kg
# See also LICENSE.txt
"""Calendar views."""

import calendar
import datetime

import persistent
import zope.annotation
import zope.app.container.contained
import zope.cachedescriptors.property
import zope.component
import zope.i18n.format
import zope.interface
import zope.security.interfaces
import zope.session.interfaces
import zope.viewlet.viewlet

import zeit.cms.browser.menu

import zeit.calendar.interfaces
import zeit.calendar.browser.interfaces
from zeit.calendar.i18n import MessageFactory as _


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

    def update(self):
        self._delete_event()
        self._register_last_view()

        # Store potential request values to session:
        self.selected_day, self.selected_month, self.selected_year

    @zope.cachedescriptors.property.Lazy
    def today(self):
        return datetime.datetime.now().date()

    @zope.cachedescriptors.property.Lazy
    def selected_date(self):
        return datetime.date(self.selected_year,
                             self.selected_month,
                             self.selected_day)

    @zope.cachedescriptors.property.Lazy
    def selected_day(self):
        now = datetime.datetime.now()
        day = self._get_request_or_session_value('day', now.day)
        return day

    @zope.cachedescriptors.property.Lazy
    def selected_month(self):
        now = datetime.datetime.now()
        month = self._get_request_or_session_value('month', now.month)
        return month

    @zope.cachedescriptors.property.Lazy
    def selected_year(self):
        now = datetime.datetime.now()
        year = self._get_request_or_session_value('year', now.year)
        return year

    def _get_request_or_session_value(self, name, default):
        value = self.request.get(name)
        if value:
            self.session[name] = value
        else:
            value = self.session.get(name)
        if not value:
            value = default
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
            event_dicts = [dict(obj=event,
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

    @zope.cachedescriptors.property.Lazy
    def session(self):
        return zope.session.interfaces.ISession(self.request)['zeit.calendar']

    @zope.cachedescriptors.property.Lazy
    def today(self):
        return datetime.date.today()

    @zope.cachedescriptors.property.Lazy
    def hidden_ressorts(self):
        last_view = zeit.calendar.browser.interfaces.ILastView(
            self.request.principal, None)
        if last_view is None:
            return ()
        return last_view.hidden_ressorts


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
        start = self.day_list[0]
        end = self.day_list[-1]
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
        weekdays = []
        for day in self.day_list:
            weekdays.append(formatter.format(day, pattern))
        return weekdays

    @zope.cachedescriptors.property.Lazy
    def selected_week_calendar(self):
        result = []
        for day in self.day_list:
            result.append(self._get_day_dict(day))
        return result

    @zope.cachedescriptors.property.Lazy
    def day_list(self):
        start_date = self.selected_date - datetime.timedelta(days=1)
        end_date = self.selected_date + datetime.timedelta(days=7)
        days = []
        while start_date < end_date:
            days.append(start_date)
            start_date += datetime.timedelta(days=1)
        return days

    @zope.cachedescriptors.property.Lazy
    def forward(self):
        return self.selected_date + datetime.timedelta(days=1)

    @zope.cachedescriptors.property.Lazy
    def backward(self):
        return self.selected_date - datetime.timedelta(days=1)

    @zope.cachedescriptors.property.Lazy
    def fastforward(self):
        return self.selected_date + datetime.timedelta(days=7)

    @zope.cachedescriptors.property.Lazy
    def fastbackward(self):
        return self.selected_date - datetime.timedelta(days=7)


class Sidebar(zope.viewlet.viewlet.ViewletBase):
    """Calendar sitebar view."""

    @zope.cachedescriptors.property.Lazy
    def calendar(self):
        calendar = zope.component.getUtility(
            zeit.calendar.interfaces.ICalendar)
        view = zope.component.getMultiAdapter(
            (calendar, self.request),
            name='month.html')
        return view


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
