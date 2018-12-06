import grok
import uvcsite.cataloging
import uvcsite.plugins
import uvcsite.plugins.subplugins
from uvcsite.utils.script_helpers import getContentInAllFolders
from zope.catalog.interfaces import ICatalog
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds
from zope.authentication.interfaces import IAuthentication
from zope.pluggableauth.interfaces import IAuthenticatorPlugin
from zope.lifecycleevent import ObjectModifiedEvent

from .auth import UserAuthenticatorPlugin
from .indexes import QAHUsersCatalog
from .interfaces import QAHDeployment


class QAHPlugin(uvcsite.plugins.ComplexPlugin):
    grok.name('ukh.qah')

    fa_icon = 'book'
    title = u"Qah plugins"
    description = u"Qah"
    
    subplugins = {
        'catalog': uvcsite.plugins.subplugins.Cataloger(
            QAHUsersCatalog, QAHDeployment),
        'authenticator': uvcsite.plugins.subplugins.PAUComponent(
            UserAuthenticatorPlugin, 'authenticator')
        }

    @uvcsite.plugins.plugin_action(
        'Diagnostic', uvcsite.plugins.States.INSTALLED)
    def diagnose(self, site):
        value = self.subplugins['catalog'].diagnose(site)
        return uvcsite.plugins.Result(
            value=value,
            type=uvcsite.plugins.ResultTypes.JSON,
            redirect=False)

    @uvcsite.plugins.plugin_action(
        'Recatalog', uvcsite.plugins.States.INSTALLED)
    def recatalog(self, site):

        def iter_docs(site):
            for hf in site['members'].values():
                documents = hf.get('Documents')
                if documents:
                    for doc in documents.values():
                        yield doc

        nb = self.subplugins['catalog'].recatalog(site, iter_docs(site))
        return uvcsite.plugins.Result(
            value=u'%s users recataloged !' % nb,
            type=uvcsite.plugins.ResultTypes.MESSAGE,
            redirect=True)

    @uvcsite.plugins.plugin_action(
        'Install', uvcsite.plugins.States.NOT_INSTALLED,
        uvcsite.plugins.States.INCONSISTANT)
    def install(self, site):
        return self.dispatch('install', site)
    
    @uvcsite.plugins.plugin_action(
        'Uninstall', uvcsite.plugins.States.INSTALLED,
        uvcsite.plugins.States.INCONSISTANT)
    def uninstall(self, site):
        return self.dispatch('uninstall', site)
