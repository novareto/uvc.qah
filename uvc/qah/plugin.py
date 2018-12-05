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


class QAHPlugin(uvcsite.plugins.Plugin):
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

    @property
    def status(self):
        statuses = [sp.status for sp in self.subplugins.values()]
        states = set((s.state for s in statuses))
        if len(states) > 1:
            status = uvcsite.plugins.Status(
                state=uvcsite.plugins.States.INCONSISTANT)
        elif uvcsite.plugins.States.INSTALLED in states:
            status = uvcsite.plugins.Status(
                state=uvcsite.plugins.States.INSTALLED)
        else:
            status = uvcsite.plugins.Status(
                state=uvcsite.plugins.States.NOT_INSTALLED)

        for s in statuses:
            if s.infos:
                status.infos.extend(s.infos)

        return status

    @uvcsite.plugins.plugin_action(
        'Install', uvcsite.plugins.States.NOT_INSTALLED,
        uvcsite.plugins.States.INCONSISTANT)
    def install(self, site):
        errors = []
        for sp in self.subplugins.values():
            try:
                sp.install(site)
            except uvcsite.plugins.PluginError as exc:
                errors.extend(exc.messages)

        if errors:
            raise uvcsite.plugins.PluginError(
                u'QAH installation encountered errors', *errors)

        return uvcsite.plugins.Result(
            value=u'QAH installed with success',
            type=uvcsite.plugins.ResultTypes.MESSAGE,
            redirect=True)

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
        'Uninstall', uvcsite.plugins.States.INSTALLED,
        uvcsite.plugins.States.INCONSISTANT)
    def uninstall(self, site):
        errors = []
        for sp in self.subplugins.values():
            try:
                sp.uninstall(site)
            except uvcsite.plugins.PluginError as exc:
                errors.extend(exc.errors)

        if errors:
            raise uvcsite.plugins.PluginError(
                u'QAH uninstallation encountered errors', *errors)

        return uvcsite.plugins.Result(
            value=u'QAH uninstalled with success',
            type=uvcsite.plugins.ResultTypes.MESSAGE,
            redirect=True)
