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
from zope.location import Location


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
        grok.notify(grok.ObjectAddedEvent(anno))  # BBB Triggers Workflow ?
