import grok
import uvcsite
import base64
from Crypto.Cipher import AES
from zope import schema
from zope.interface import Interface, implementer
from zope.pluggableauth.factories import Principal
from zope.pluggableauth import interfaces
from zope.catalog.interfaces import ICatalog
from zope.component import queryUtility
from zope.publisher.interfaces import IRequest
from zope.publisher.browser import applySkin
from .skin import ITemporarySkin


MASTER_KEY = "EykibucoiHaucpajekOfjevramemUkijBergEmIjyeb8Okoj"


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


@implementer(interfaces.IPrincipalInfo)
class TemporaryInfo:

    def __init__(self, id, document):
        self.id = id
        self.title = id
        self.description = id
        self.document = document


class TemporaryPrincipal(Principal):

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document', None)
        Principal.__init__(self, *args, **kwargs)


@implementer(interfaces.IAuthenticatorPlugin)
class UserAuthenticatorPlugin(grok.GlobalUtility):
    grok.name("temporary_users")

    required = {'login', 'password'}
    
    def getAccount(self, id):
        catalog = queryUtility(ICatalog, name="qah.users_catalog")
        if catalog is None:
            return None
        users = list(catalog.searchResults(uid=(id, id)))
        if users:
            assert len(users) == 1
            return users[0]
        return None

    def authenticateCredentials(self, credentials):

        # Empty or malformed credentials are ignored.
        if not credentials or (self.required - set(credentials)):
            return
        
        account = self.getAccount(credentials['login'])
        if account is not None:
            token = encrypt('%(login)s:%(password)s' % credentials)
            if account.token == token:
                return TemporaryInfo(id=account.uid, document=account)
        return None

    def principalInfo(self, id):
        account = self.getAccount(id)
        if account is None:
            return
        return TemporaryInfo(id=account.uid, document=account)


@implementer(interfaces.IAuthenticatedPrincipalFactory)
class TemporaryInfoFactory(grok.MultiAdapter):
    grok.adapts(TemporaryInfo, IRequest)

    def __init__(self, info, request):
        self.info = info
        self.request = request

    def __call__(self, authentication):
        principal = TemporaryPrincipal(
            authentication.prefix + self.info.id,
            self.info.title,
            self.info.description,
            document=self.info.document
        )
        grok.notify(interfaces.AuthenticatedPrincipalCreated(
            authentication, principal, self.info, self.request))
        applySkin(self.request, ITemporarySkin)
        return principal
