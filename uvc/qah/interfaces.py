import zope.interface
import zope.schema
import zope.component


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


class IQAHDeployment(zope.component.interfaces.IObjectEvent):
    pass


@zope.interface.implementer(IQAHDeployment)
class QAHDeployment(zope.component.interfaces.ObjectEvent):
    pass
