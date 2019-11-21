# -*- coding: utf-8 -*-
# # Copyright (c) 2007-2019 NovaReto GmbH
# # cklinger@novareto.de

import uvcsite
import grok
from .product import ITemporaryUser, IPassword
from zope.interface import alsoProvides, implementer
from .product import encrypt
from grokcore.annotation import Annotation
from zope.interface import implementer
from zeam.form.base import makeAdaptiveDataManager
from dolmen.forms.base.utils import set_fields_data


@implementer(ITemporaryUser)
class CredentialsAnnotation(Annotation):
    grok.context(uvcsite.IContent)


class AddSpecialUser(uvcsite.Form):
    grok.context(uvcsite.IContent)

    title = u"Einmal Passwort"
    label = u"Einmal Passwort"
    description = u"Beschreibung"

    #dataManager = makeAdaptiveDataManager(ITemporaryUser)

    fields = uvcsite.Fields(ITemporaryUser, IPassword).omit('token')

    @uvcsite.action(u'Benutzer erstellen')
    def handle_save(self):
        data, errors = self.extractData()
        if errors:
            return
        alsoProvides(self.context, ITemporaryUser)
        anno = ITemporaryUser(self.context)
        token = encrypt('%s:%s' % (data['uid'], data['password']))
        #set_fields_data(self.fields, self.getContentData(), data)
        anno.token = token
        anno.uid = data['uid']
        anno.email = data['email']
        grok.notify(grok.ObjectAddedEvent(self.context))  # BBB Triggers Workflow ?
