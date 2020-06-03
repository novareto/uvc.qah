#import grok
#import uvcsite
#from uvc.qah.skin import ITemporarySkin
#from zope.component import getMultiAdapter
#from zope.interface import Interface
#from guv.exskin.layout import GuvExLayout
#from guv.exskin.resources import SkinViewlet
#from uvc.layout.slots.menus import GlobalMenu, PersonalMenu, PersonalPreferences
#from uvc.layout.slots.menuviewlets import PersonalPreferencesViewlet
#from uvc.tbskin.views import WizardTemplate
#
#
#class TemporaryLayout(GuvExLayout):
#    grok.layer(ITemporarySkin)
#
#
#
#class SkinViewlet(SkinViewlet):
#    grok.layer(ITemporarySkin)
#
#    def update(self):
#        super(SkinViewlet, self).update()
#
#
#
#class QAHTraverser(grok.Traverser):
#    grok.context(uvcsite.IUVCSite)
#    grok.layer(ITemporarySkin)
#
#    def traverse(self, name):
#        return self.request.principal.document.__parent__
#
#
#class TemporaryHome(uvcsite.Page):
#    grok.name("index")
#    grok.context(uvcsite.IUVCSite)
#    grok.layer(ITemporarySkin)
#
#    def render(self):
#        url = "%s/%s/start-wf" %(self.application_url(), self.request.principal.document.__parent__.__name__)
#        return self.redirect(url)
#
#
#
#class WizardTemplate(WizardTemplate):
#    grok.layer(ITemporarySkin)
#
#
#class GlobalMenu(GlobalMenu):
#    grok.layer(ITemporarySkin)
#
#    def filter(self, viewlets):
#        items = super(GlobalMenu, self).filter(viewlets)
#        return [
#            (name, viewlet)
#            for name, viewlet in items
#            if ITemporarySkin.providedBy(viewlet)
#        ]
#
#
#class PersonalPreferences(PersonalPreferences):
#    grok.layer(ITemporarySkin)
#    grok.baseclass()
#
#    def update(self):
#        super(PersonalPreferences, self).update()
#
#    def filter(self, viewlets):
#        items = super(PersonalPreferences, self).filter(viewlets)
#        return [
#            (name, viewlet)
#            for name, viewlet in items
#            if ITemporarySkin.providedBy(viewlet)
#        ]
#
#class PersonalPreferencesViewlet(PersonalPreferencesViewlet):
#    grok.layer(ITemporarySkin)
#
#    def render(self):
#        return ""
