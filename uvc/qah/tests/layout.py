import grokcore.layout
from grokcore.component import name, context
from zope.interface import Interface


class Layout(grokcore.layout.Layout):
    name('')
    context(Interface)

    def __call__(self, view):
        return u"<html>\n" + unicode(view.render())

    def render(self):
        return u""
