# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2019 NovaReto GmbH
# # cklinger@novareto.de

import grok
import uvcsite


from .interfaces import ITemporaryUser, IPassword
from zope.interface import implementer
from .auth import encrypt
from .skin import ITemporarySkin
from grokcore.annotation import Annotation
from dolmen.forms.base.utils import set_fields_data
from zope.location import Location
from zope.securitypolicy.interfaces import IPrincipalRoleManager


grok.templatedir('templates')


@implementer(ITemporaryUser)
class CredentialsAnnotation(Annotation, Location):
    grok.provides(ITemporaryUser)
    grok.context(uvcsite.IContent)


class AddSpecialUser(uvcsite.Form):
    grok.context(uvcsite.IContent)

    title = u"Einmal Passwort"
    label = u"Einmal Passwort"
    description = u"Beschreibung"

    fields = uvcsite.Fields(ITemporaryUser, IPassword).omit('token')

    @uvcsite.action(u'Benutzer erstellen')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            return
        token = encrypt('%s:%s' % (data['uid'], data['password']))
        anno = ITemporaryUser(self.context)
        set_fields_data(self.fields, anno, data)
        anno.token = token
        grok.notify(grok.ObjectAddedEvent(anno))
        prm = IPrincipalRoleManager(self.context)
        prm.assignRoleToPrincipal('uvc.Editor', data['uid'])
        print "I SET THE ROLE HERE"
        self.flash(u'Der neue Benutzer %s wurde erfolgreich angelegt' % data['uid'])
        self.redirect(self.url(self.context, 'showspecialuser'))
        

class ShowSpecialUser(uvcsite.Page):
    grok.context(uvcsite.IContent)

    def update(self):
        self.user = ITemporaryUser(self.context)


#class TemporaryHome(grok.View):
#    grok.name('index')
#    grok.context(uvcsite.IUVCSite)
#    grok.layer(ITemporarySkin)
#
#    def render(self):
#        url = self.url(self.request.principal.document.__parent__, 'edit')
#        self.flash(u'Bitte füllen Sie die folgenden Felder')
#        self.redirect(url)
