import grok
from zope.interface import implementer
from uvcsite import IUVCSite, IContent

from .product import ITemporaryUser
from .interfaces import IQAHDeployment


@implementer(ITemporaryUser)
class UserContent(grok.Adapter):
    grok.context(IContent)
    grok.baseclass()

    @property
    def uid(self):
        anno = ITemporaryUser(self.context)
        return anno.uid

    @property
    def token(self):
        anno = ITemporaryUser(self.context)
        return anno.token

    @property
    def email(self):
        anno = ITemporaryUser(self.context)
        return anno.email


class QAHUsersCatalog(grok.Indexes):
    grok.context(ITemporaryUser)
    grok.name('qah.users_catalog')
    grok.site(IUVCSite)
    grok.install_on(IQAHDeployment)

    uid = grok.index.Field()
    token = grok.index.Field()
    email = grok.index.Field()
