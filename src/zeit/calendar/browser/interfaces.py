
import zope.interface
import zope.schema


class ILastView(zope.interface.Interface):

    last_view = zope.schema.ASCIILine(
        title=u"The last calendar view the user has visited.")

    hidden_ressorts = zope.schema.FrozenSet(
        title=u"Ressors that are hidden.")
