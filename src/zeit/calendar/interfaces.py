# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt
"""Calendar interfaces.

To some extent inspired by schooltool.

"""

import zope.app.container.interfaces
import zope.app.security.vocabulary
import zope.interface
import zope.schema

import zeit.cms.content.contentsource
import zeit.cms.content.sources

import zeit.calendar.source
from zeit.calendar.i18n import MessageFactory as _


class EndBeforeStart(zope.schema.ValidationError):

    def doc(self):
        return _('The event ends before it starts.')



class ICalendarEvent(zope.interface.Interface):
    """An event."""

    start = zope.schema.Date(
        title=_("Start"),
        description=_("Date when the event starts."))

    end = zope.schema.Date(
        title=_("End"),
        description=_("Date when the event ends."),
        required=False)

    title = zope.schema.TextLine(
        title=_("Title"),
        description=_("Title will be shown in overview pages."))

    description = zope.schema.Text(
        title=_("Description"),
        required=False)

    related = zope.schema.Tuple(
        title=_("Related content"),
        description=_("Documents that are related to this object."),
        default=(),
        required=False,
        value_type=zope.schema.Choice(
            source=zeit.cms.content.contentsource.cmsContentSource))

    location = zope.schema.TextLine(
        title=_("Location/Type"),
        description=_("Where should the article be placed."),
        required=False)

    ressort = zope.schema.Choice(
        title=_('Ressort'),
        source=zeit.cms.content.sources.NavigationSource(),
        required=False)

    thema = zope.schema.Bool(
        title=_("Topic?"),
        description=_("Is the article a topic for the next week?"))

    completed = zope.schema.Bool(
        title=_('Completed?'),
        description=_('Check when the event has been completed.'),
        default=False)

    added_by = zope.schema.Choice(
        title=_('Added by'),
        readonly=True,
        source=zope.app.security.vocabulary.PrincipalSource())

    priority = zope.schema.Choice(
        title=_('Priority'),
        required=False,
        source=zeit.calendar.source.PrioritySource())

    @zope.interface.invariant
    def start_before_end(self):
        if not self.end:
            return True
        if self.start <= self.end:
            return True
        raise EndBeforeStart(self.start, self.end)


class ICalendar(zope.app.container.interfaces.IReadContainer):
    """Calendar."""

    def getEvents(date):
        """Return the events occuring on `date`.

        date: datetime.date object.

        """

    def haveEvents(date):
        """Return whether there are events occuring on `date`.

        date: datetime.date object.

        """


class IEditCalendar(zope.app.container.interfaces.IWriteContainer):
    pass


class IRessortGroupManager(zope.interface.Interface):

    groups = zope.interface.Attribute(
        """A list of dicts. Each entry has the following keys:
        - title
        - css_class
        - ressorts: list of ressort names
        """)

    def css(ressort):
        """returns the css class for the given ressort."""
