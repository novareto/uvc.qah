# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de

import grok
import random
import uvcsite
import transaction
import zope.schema
import base64
import json
import urllib

from uuid import uuid4
from BTrees.OOBTree import OOBTree
from Crypto.Cipher import AES

from . import REPORTS_FOLDER

from dolmen.forms.base import apply_data_event
from uvcsite.interfaces import IMyHomeFolder
from uvcsite.interfaces import IUVCSite
from zeam.form import base
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.interface import Interface, implementer
from zope.intid import IIntIds
from zope.location import Location
from zope.publisher.interfaces import browser
from zope.security.management import checkPermission
from zope.traversing.interfaces import ITraversable


MASTER_KEY = "EykibucoiHaucpajekOfjevramemUkijBergEmIjyeb8Okoj"
NO_CONTEXT = False
CONTEXT = True
NO_PERMISSION = 'zope.Public'


def encrypt(text):
    enc_secret = AES.new(MASTER_KEY[:32])
    tag_string = (str(text) +
                  (AES.block_size -
                   len(str(text)) % AES.block_size) * "\0")
    cipher_text = base64.b64encode(enc_secret.encrypt(tag_string))
    return cipher_text


def decrypt(cipher):
    dec_secret = AES.new(MASTER_KEY[:32])
    raw_decrypted = dec_secret.decrypt(base64.b64decode(cipher))
    clear_val = raw_decrypted.decode().rstrip("\0")
    return clear_val


class IResolvable(Interface):
    pass


class IShareLinks(Interface):
    pass


class IReportLogin(Interface):

    username = zope.schema.TextLine(
        title=u"Username",
    )

    password = zope.schema.TextLine(
        title=u"Password",
    )


class IOfficialReport(Interface):

    official_field_1 = zope.schema.TextLine(
        title=u"Some info",
    )

    official_field_2 = zope.schema.TextLine(
        title=u"Some more info",
    )

    official_field_3 = zope.schema.TextLine(
        title=u"Other info",
    )


class IIndividualReport(Interface):

    individual_field_1 = zope.schema.TextLine(
        title=u"Some personal info",
    )

    individual_field_2 = zope.schema.TextLine(
        title=u"Some more personal info",
    )

    individual_field_3 = zope.schema.TextLine(
        title=u"Other personal info",
    )

    
class IAccidentReport(IOfficialReport, IIndividualReport):
    pass


@implementer(IAccidentReport, IResolvable)
class Report(uvcsite.Content):
    pass


class Sharer(grok.MultiAdapter):
    grok.name('share')
    grok.provides(ITraversable)
    grok.adapts(IUVCSite, browser.IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        shares = getUtility(IShareLinks, name='shares')
        stamp = decrypt(name.decode('hex'))
        if stamp in shares:
            intid = getUtility(IIntIds, name='intids')
            shared = intid.queryObject(shares[stamp])
            if shared and IResolvable.providedBy(shared):
                return shared
        return None


def gencrap(length=8):
    s = "abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join(random.sample(s, length))
    

class AddReport(uvcsite.Form):
    grok.context(IMyHomeFolder)
    grok.require('uvc.ViewContent')

    ignoreContent = True
    fields = base.Fields(IOfficialReport)

    @staticmethod
    def generate_access():
        return gencrap(), gencrap()

    @staticmethod
    def encode_access(user, passwd):
        return base64.b64encode('%s_%s' % (user, passwd))

    def create_object(self, data):
        content = Report()
        apply_data_event(self.fields, content, data)
        self.context[str(uuid4())] = content
        user, passwd = self.generate_access()
        annotations = IAnnotations(content)
        self.flash('Added new report for user: %s, %s' % (user, passwd))
        access = self.encode_access(user, passwd)
        annotations['public_access'] = access
        return access, content

    def create_link(self, access, content):
        intid = getUtility(IIntIds, name='intids')
        shares = getUtility(IShareLinks, name='shares')
        shared = intid.getId(content)
        uid = intid.getId(content)
        shares[access] = uid

    @base.action(u'Submit')
    def submit(self):
        data, errors = self.extractData()
        if not errors:
            access, content = self.create_object(data)
            self.create_link(access, content)
            self.redirect(self.url(content))
            return base.SUCCESS
        self.errors = errors
        return base.FAILURE


class CompleteReport(uvcsite.Form):
    grok.name('index')
    grok.require('zope.Public')

    ignoreContent = False    
    fields = base.Fields(IAccidentReport)
    for field in fields:
        if field.interface is IOfficialReport:
            field.mode = base.DISPLAY

    def __init__(self, context, request):
        uvcsite.Form.__init__(self, context, request)
        self.setContentData(context)

    @base.action(u'Submit')
    def submit(self):
        data, errors = self.extractData()
        if not errors:
            apply_data_event(self.fields, self.context, data)
            return base.SUCCESS

        print errors
        return base.FAILURE


class Shared(uvcsite.Form):
    grok.context(Interface)
    grok.require('zope.Public')

    ignoreContent = True
    fields = base.Fields(IReportLogin)

    @base.action(u'Submit')
    def submit(self):
        data, errors = self.extractData()
        if not errors:
            access = AddReport.encode_access(data['username'], data['password'])
            root = grok.getApplication()
            folder = getUtility(IShareLinks, name='shares')
            if access in folder:
                # redirect me
                stamp = encrypt(access)
                self.redirect(
                    self.url(root, '++share++%s' % stamp.encode("hex")))
                return base.SUCCESS
        return base.FAILURE

        
