from plonetheme.nuplone.skin.pwreminder import PasswordReset
from zope.i18nmessageid import MessageFactory

MF = MessageFactory("nuplone")


def updateFields(self):
    super(PasswordReset, self).updateFields()
    self.fields["login"].field.title = MF(
        u"label_email", default=u"E-mail address")

PasswordReset.updateFields = updateFields
