import grok
from uvc.layout.layout import IUVCSkin
from guv.exskin.layout import IGuvExSkin


class ITemporaryLayer(grok.IDefaultBrowserLayer):
    pass


class ITemporarySkin(ITemporaryLayer):
    grok.skin('qah.temporary')
