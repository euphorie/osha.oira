from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from plonetheme.nuplone.skin import pwreminder
from ..interfaces import IOSHAContentSkinLayer
from euphorie.content import MessageFactory as _
from zope.i18n import translate


class PasswordReset(pwreminder.PasswordReset):
    grok.context(ISiteRoot)
    grok.name("reset-password")
    grok.require("zope2.Public")
    grok.layer(IOSHAContentSkinLayer)

    orig_description = pwreminder.PasswordReset.description
    extra_description = _(
        u"password_policy_conditions",
        default=u"Your password must contain at least 5 characters, "
        u"including at least one capital letter, one number and "
        u"one special character (e.g. $, # or @).")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.language = getToolByName(
            context, 'portal_languages').getPreferredLanguage()

    @property
    def description(self):
        description = u" ".join([
            translate(self.orig_description, target_language=self.language),
            translate(self.extra_description, target_language=self.language)])
        return description
