import grok
import uvcsite
from .skin import ITemporarySkin


class TemporaryHome(grok.View):
    grok.name('index')
    grok.context(uvcsite.IUVCSite)
    grok.layer(ITemporarySkin)
    
    def render(self):
        return 'Temporary user, allowed to edit: %s' % repr(self.request.principal.document)
