import grok
from uvc.layout.layout import IUVCSkin


class ITemporaryLayer(grok.IDefaultBrowserLayer):
    pass


class ITemporarySkin(ITemporaryLayer, IUVCSkin):
    grok.skin('qah.temporary')
