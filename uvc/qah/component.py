# -*- coding: utf-8 -*-
# Copyright (c) 2007-2011 NovaReto GmbH
# cklinger@novareto.de

import grok
import uvcsite
import transaction
import zope.schema
import base64
import json
import urllib

from BTrees.OOBTree import OOBTree
from Crypto.Cipher import AES
from uuid import uuid4

from dolmen.forms.base import apply_data_event
from uvcsite.interfaces import IUVCSite
from zeam.form import base
from zope.annotation import IAnnotations
from zope.interface import Interface, implementer
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


def make_stamp(**stamp_info):
    return encrypt(json.dumps(stamp_info))


def read_stamp(stamp):
    return json.loads(decrypt(stamp))


class IShared(uvcsite.IContent):

    name = zope.schema.TextLine(
        title=u"Name",
    )

    alter = zope.schema.TextLine(
        title=u"Alter",
    )


@implementer(IShared)
class Shared(uvcsite.Content):
    pass


class FormStorage(Location):

    def __init__(self, storage, parent, name=''):
        self.storage = storage
        self.__name__ = '++shareform++%s' % name
        self.__parent__ = parent
        print name
        if name:
            self.stamp = read_stamp(name)
        else:
            self.stamp = {}

    def get_content(self):
        assert self.stamp
        uid = self.stamp['uid']
        return self.storage.get(uid)

    def set_content(self, content):
        if self.stamp:
            uid = self.stamp['uid']
        else:
            uid = str(uuid4())
        self.storage[uid] = content
        return uid


class ShareFormTraverser(grok.MultiAdapter):
    grok.name('shareform')
    grok.provides(ITraversable)
    grok.adapts(IUVCSite, browser.IBrowserRequest)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        annotations = IAnnotations(self.context, None)
        if annotations is None:
            raise NotImplementedError('Annotations access failed')
        if 'shareform' not in annotations:
            annotations['shareform'] = OOBTree()

        storage = FormStorage(
            annotations['shareform'], self.context, name)
        return storage


class MyShare(uvcsite.Form):
    grok.context(FormStorage)
    grok.require('zope.Public')

    defaultStep = 'init'
    nextStep = None
    ignoreContent = False
    steps = {
        defaultStep: (NO_CONTEXT, 'uvc.ViewContent', ['name'], 'resume'),
        'resume': (CONTEXT, 'zope.Public', ['alter'], None),
    }

    def __init__(self, context, request):
        step = context.stamp.get('step', self.defaultStep)
        step_args = self.steps.get(step)
        if step_args is None:
            raise NotImplementedError('Unknown step')
        with_content, permission, fieldnames, nextStep = step_args
        if (permission != NO_PERMISSION and
            not checkPermission(permission, context)):
            raise NotImplementedError('Missing required permission')
        if with_content:
            assert context.stamp
            # Here, we need to restore the saved object using the stamp info
            content = context.get_content()
        else:
            content = Shared()

        uvcsite.Form.__init__(self, context, request)
        self.setContentData(content)
        self.fields = base.Fields(IShared)
        if not with_content:
            self.fields = self.fields.select(*fieldnames)
        else:
            for field in self.fields:
                if field.identifier not in fieldnames:
                    field.mode = base.DISPLAY
        self.nextStep = nextStep

    def save(self, content):
        """Temporary save, the time to complete it.
        """
        uid = self.context.set_content(content)
        args = {'uid': uid, 'step': self.nextStep}
        stamp = make_stamp(**args)
        print "Next step is ++shareform++%s/@@myshare" % urllib.quote_plus(stamp)

    def persist(self, content):
        """Object is completed, persist it definitively.
        """
        print "Persisted."

    @base.action(u'Submit')
    def submit(self):
        data, errors = self.extractData()
        content = self.getContent()
        apply_data_event(self.fields, content, data)
        if not self.nextStep:
            self.persist(content)
        else:
            self.save(content)
        return
