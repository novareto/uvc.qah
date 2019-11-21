# -*- coding: utf-8 -*-

import grok
from uvcsite import IUVCSite

from .interfaces import ITemporaryUser
from .interfaces import IQAHDeployment


class QAHUsersCatalog(grok.Indexes):
    grok.context(ITemporaryUser)
    grok.name('qah.users_catalog')
    grok.site(IUVCSite)
    grok.install_on(IQAHDeployment)

    uid = grok.index.Field()
    token = grok.index.Field()
    email = grok.index.Field()
