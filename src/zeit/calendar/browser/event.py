# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime

import gocept.form.action
import gocept.form.grouped
import zope.formlib.form

import zeit.cms.browser.form
import zeit.cms.browser.interfaces
import zeit.cms.browser.view
import zeit.cms.repository.interfaces

import zeit.calendar.event
import zeit.calendar.interfaces
from zeit.calendar.i18n import MessageFactory as _


class EventFormBase(object):

    field_groups = (
        gocept.form.grouped.Fields(
            _("Event"),
            ('start', 'end', 'location', 'priority', 'thema',
             'added_by'),
            css_class='column-left-small'),
        gocept.form.grouped.Fields(
            _('Description'),
            ('ressort', 'title', 'description'),
            css_class='column-right-small'),
        gocept.form.grouped.Fields(
            _('Related'),
            ('related', ),
            css_class="full-width wide-widgets"))

    form_fields = zope.formlib.form.Fields(
        zeit.calendar.interfaces.ICalendarEvent).omit('completed')

    def nextURLForEvent(self, event):
        url = zope.component.getMultiAdapter(
            (event.__parent__, self.request), name='absolute_url')()
        start = event.start
        year = start.year
        month = start.month
        day = start.day
        return '%s?year:int=%d&month:int=%d&day:int=%d' % (
            url, year, month, day)


class AddForm(EventFormBase, zeit.cms.browser.form.AddForm):

    title = _('Add event')
    factory = zeit.calendar.event.Event
    form_fields = EventFormBase.form_fields.omit('added_by')
    cancel_next_view = 'index.html'

    def create(self, data):
        obj = super(AddForm, self).create(data)
        obj.added_by = self.request.principal.id
        return obj

    def suggestName(self, event):
        return event.title

    def nextURL(self):
        return self.nextURLForEvent(self._created_object)


class EditForm(EventFormBase, zeit.cms.browser.form.EditForm):

    title = _('Edit event')

    @zope.formlib.form.action(
        _("Apply"),
        condition=zope.formlib.form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        super(EditForm, self).handle_edit_action.success(data)
        self.request.response.redirect(self.nextURL())
        return "Redirect..."


    @gocept.form.action.confirm(
        _('Delete event'),
        confirm_message=_('Really delete event?'))
    def handle_delete_action(self, action, data):
        next_url = self.nextURL()
        del self.context.__parent__[self.context.__name__]
        self.send_message(_('Event deleted.'))
        self.redirect(next_url)
        return "Redirect..."

    def nextURL(self):
        return self.nextURLForEvent(self.context)


@zope.component.adapter(
    zeit.calendar.interfaces.ICalendar,
    zeit.cms.content.interfaces.ICMSContentSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def calendar_browse_location(context, schema):
    """Deduce location from current date."""
    return get_location_for(datetime.datetime.now())


@zope.component.adapter(
    zeit.calendar.interfaces.ICalendarEvent,
    zeit.cms.content.interfaces.ICMSContentSource)
@zope.interface.implementer(
    zeit.cms.browser.interfaces.IDefaultBrowsingLocation)
def event_browse_location(context, schema):
    """Get the location from the event start."""
    return get_location_for(context.start)


def get_location_for(date):
    year = date.year
    volume = date.strftime('%W')

    unique_id = u'http://xml.zeit.de/online/%s/%s' % (year, volume)

    repository = zope.component.getUtility(
        zeit.cms.repository.interfaces.IRepository)
    try:
        return repository.getContent(unique_id)
    except KeyError:
        return repository


class CompleteEvent(zeit.cms.browser.view.Base):

    def __call__(self):
        self.context.completed = True
        self.send_message(_('Event completed.'))
        self.redirect(self.url(self.context.__parent__))


class UncompleteEvent(zeit.cms.browser.view.Base):

    def __call__(self):
        self.context.completed = False
        self.send_message(_('Event reactivated.'))
        self.redirect(self.url(self.context.__parent__))
