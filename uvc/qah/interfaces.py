import zope.interface
import zope.component


class IQAHDeployment(zope.component.interfaces.IObjectEvent):
    pass


@zope.interface.implementer(IQAHDeployment)
class QAHDeployment(zope.component.interfaces.ObjectEvent):
    pass
