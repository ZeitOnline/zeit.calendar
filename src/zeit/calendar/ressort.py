# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.cache.method
import gocept.lxml.objectify
import logging
import urllib2
import zeit.calendar.interfaces
import zope.interface


log = logging.getLogger(__name__)


class RessortGroupManager(object):

    zope.interface.implements(zeit.calendar.interfaces.IRessortGroupManager)

    def __init__(self):
        self._groups = []
        self._css = {}
        self.misc_class = ''

    @gocept.cache.method.Memoize(600)
    def get_groups(self):
        result = []
        config = zope.app.appsetup.product.getProductConfiguration(
            'zeit.calendar')
        url = config['ressortgroup-url']
        root = gocept.lxml.objectify.fromfile(urllib2.urlopen(url))
        log.info('Loading ressort groups from %s' % url)
        for group in root.iterchildren(tag='group'):
            item = {}
            item['title'] = group.get('title')
            item['css_class'] = group.get('css_class')
            item['ressorts'] = []
            for ressort in group.iterchildren():
                item['ressorts'].append(ressort.get('name'))
            result.append(item)

        result.append(dict(title=root.misc.get('title'),
                           css_class=root.misc.get('css_class')))
        self.misc_class = root.misc.get('css_class')
        return result

    def _load(self):
        try:
            self._groups = self.get_groups()
            self._css.clear()
            for item in self._groups:
                for ressort in item.get('ressorts', []):
                    self._css[ressort] = item['css_class']
        except Exception, e:
            log.exception(e)

    @property
    def groups(self):
        self._load()
        return self._groups

    def css(self, ressort):
        self._load()
        return self._css.get(ressort, self.misc_class)
