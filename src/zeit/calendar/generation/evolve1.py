# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import zope.component

import zeit.cms.generation

import zeit.calendar.interfaces


@zeit.cms.generation.get_root
def evolve(root):
    calendar = zope.component.getUtility(zeit.calendar.interfaces.ICalendar)
    key_index = calendar._key_index
    for key, day in key_index.items():
        key_index[key] = (day, None)
