import grok
from uvcsite import IUVCSite

from .product import ITemporaryUser
from .interfaces import IQAHDeployment


class QAHUsersCatalog(grok.Indexes):
    grok.context(ITemporaryUser)
    grok.name('qah.users_catalog')
    grok.site(IUVCSite)
    grok.install_on(IQAHDeployment)

    uid = grok.index.Field()
    token = grok.index.Field()
