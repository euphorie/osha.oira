from five import grok
from osha.oira.interfaces import IOSHAContentSkinLayer
from plonetheme.nuplone.skin import login
from plonetheme.nuplone.skin import pwreminder
from Products.CMFCore.interfaces import ISiteRoot
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface

MF = MessageFactory("nuplone")

grok.templatedir("templates")


class Login(login.Login):
    """ Override so that we can have our own template.
    """
    grok.context(Interface)
    grok.layer(IOSHAContentSkinLayer)
    grok.name("login")
    grok.template("login")


class OSHARequestPasswordForm(pwreminder.RequestPasswordForm):
    """ Override so that we can change some labels
    """
    grok.context(ISiteRoot)
    grok.layer(IOSHAContentSkinLayer)
    grok.name("request-password-reset")

    def updateFields(self):
        super(OSHARequestPasswordForm, self).updateFields()
        self.fields["login"].field.title = MF(
            u"label_email", default=u"E-mail address")


# XXX
# The following leads to a Configuration Conflict Error on startup
# Therefore the required piece of code is now located in
# patch_passwordreset.py

# class OSHAPasswordReset(pwreminder.PasswordReset):
#     """ Override so that we can change some labels
#     """
#     grok.context(ISiteRoot)
#     grok.layer(IOSHAContentSkinLayer)
#     grok.name("reset-password")

#     def updateFields(self):
#         super(OSHAPasswordReset, self).updateFields()
#         self.fields["login"].field.title = MF(
#             u"label_email", default=u"E-mail address")
