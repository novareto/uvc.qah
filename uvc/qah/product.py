import grok
import uvcsite
import transaction
import zope.schema
import zope.interface
import zope.component
import zope.security

from dolmen.forms.base import Fields
from uvcsite.content.directive import productfolder
from uvcsite.content.views import Add as BaseAdd
from uvcsite.content.productregistration import ProductMenuItem
from uvcsite.content.productregistration import ProductRegistration

from .auth import encrypt


class IDocuments(uvcsite.IProductFolder):
    """ Marker Interface """


class IPassword(zope.interface.Interface):

    password = zope.schema.Password(
        title=u"Password",
        required=True
    )


class ITemporaryUser(zope.interface.Interface):

    uid = zope.schema.TextLine(
        title=u"Username",
        required=True
    )

    email = zope.schema.TextLine(
        title=u"Email",
        required=True
    )

    token = zope.schema.ASCIILine(
        title=u"Access token",
        required=False
    )


class IDocument(ITemporaryUser, uvcsite.IContent):

    name = zope.schema.TextLine(
        title=u"Name",
        description=u"Name",
    )

    alter = zope.schema.TextLine(
        title=u"Alter",
        description=u"Wie ist ihr Alter",
        required=False,
    )


@zope.interface.implementer(IDocument)
class Document(uvcsite.Content):
    grok.name(u'document')
    uvcsite.schema(IDocument)

    def checkPassword(self, password):
        token = encrypt('%s:%s' % (self.uid, password))
        return token == self.token


@zope.interface.implementer(IDocuments)
class Documents(uvcsite.ProductFolder):
    grok.name('documents')
    grok.title('Documents')
    grok.description('Documents')
    uvcsite.contenttype(Document)


class DocumentsRegistration(ProductRegistration):
    grok.name('documents')
    grok.title('Documents')
    grok.description('Documents library')
    productfolder('uvc.qah.product.Documents')


class AddMenuEntry(ProductMenuItem):
    grok.name('new_document')
    grok.title('New Document')
    grok.context(zope.interface.Interface)
    grok.viewletmanager(uvcsite.IGlobalMenu)

    @property
    def reg_name(self):
        return "documents"


class Add(BaseAdd):
    grok.context(IDocuments)
    grok.require('uvc.AddContent')

    @property
    def fields(self):
        return Fields(IDocument, IPassword).omit('token')

    def create(self, data):
        password = data.pop('password')
        token = encrypt('%s:%s' % (data['uid'], password))
        content = BaseAdd.create(self, data)
        content.token = token
        return content
