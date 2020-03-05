import grok
import uvcsite
from .skin import ITemporarySkin
from zope.component import getMultiAdapter
from zope.interface import Interface
from guv.exskin.layout import GuvExLayout
from guv.exskin.resources import SkinViewlet
from uvc.layout.slots.menus import GlobalMenu
from uvc.tbskin.views import WizardTemplate


class TemporaryLayout(GuvExLayout):
    grok.layer(ITemporarySkin)


class SkinViewlet(SkinViewlet):
    grok.layer(ITemporarySkin)



class QAHTraverser(grok.Traverser):
    grok.context(uvcsite.IUVCSite)
    grok.layer(ITemporarySkin)

    def traverse(self, name):
        return self.request.principal.document.__parent__


class TemporaryHome(uvcsite.Page):
    grok.name("index")
    grok.context(uvcsite.IUVCSite)
    grok.layer(ITemporarySkin)

#    def update(self):
#        self.form = getMultiAdapter(
#            (self.request.principal.document.__parent__, self.request),
#            Interface,
#            name="start-wf",
#        )
#        #self.form.updateForm()

    def render(self):
        url = "%s/%s/start-wf" %(self.application_url(), self.request.principal.document.__parent__.__name__)
        return self.redirect(url)
#        return self.form._render_template()


class WizardTemplate(WizardTemplate):
    grok.layer(ITemporarySkin)


class GlobalMenu(GlobalMenu):
    grok.layer(ITemporarySkin)

    def filter(self, viewlets):
        items = super(GlobalMenu, self).filter(viewlets)
        #return items
        #import pdb; pdb.set_trace()
        return [
            (name, viewlet)
            for name, viewlet in items
            if ITemporarySkin.providedBy(viewlet)
        ]
