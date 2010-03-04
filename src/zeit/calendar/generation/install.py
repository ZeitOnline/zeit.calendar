# Copyright (c) 2007-2010 gocept gmbh & co. kg
# See also LICENSE.txt

import zeit.cms.generation
import zeit.cms.generation.install

import zeit.calendar.calendar
import zeit.calendar.interfaces


@zeit.cms.generation.get_root
def evolve(root):
    zeit.cms.generation.install.installLocalUtility(
        root, zeit.calendar.calendar.Calendar,
        'calendar', zeit.calendar.interfaces.ICalendar)
