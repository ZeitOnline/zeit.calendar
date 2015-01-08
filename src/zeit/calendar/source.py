
from zeit.calendar.i18n import MessageFactory as _
import zc.sourcefactory.basic


class PrioritySource(zc.sourcefactory.basic.BasicSourceFactory):

    values = (
        (1, _('^^ mandatory')),
        (0, _('^ important')),
        (-1, _('> suggestion')))

    titles = dict(values)

    def getValues(self):
        return (v[0] for v in self.values)

    def getTitle(self, value):
        return self.titles[value]
