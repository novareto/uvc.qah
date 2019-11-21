# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2019 NovaReto GmbH
# # cklinger@novareto.de


import grok
import uvcsite
from .skin import ITemporarySkin


class TemporaryHome(grok.View):
    grok.name('index')
    grok.context(uvcsite.IUVCSite)
    grok.layer(ITemporarySkin)
    
    def render(self):
        url = self.url(self.request.principal.document, 'edit')
        self.flash(u'Bitte füllen Sie die folgenden Felder')
        self.redirect(url)
