from .. import _
from Products.Archetypes.utils import IStatusMessage
from Products.MailHost.MailHost import MailHostError
from euphorie.content import user
from euphorie.content.user import IUser
from euphorie.content.user import InvalidPasswordError
from five import grok
from osha.oira.content.statistics import IOSHAContentSkinLayer
from p01.widget.password.interfaces import IPasswordConfirmationWidget
from plone import api
from plonetheme.nuplone.utils import createEmailTo
from z3c.form.interfaces import IForm
from z3c.form.interfaces import IValidator
from z3c.form.interfaces import IAddForm
from zope import component
from zope import schema
from zope.i18n import translate
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectAddedEvent
import logging
import socket

log = logging.getLogger(__name__)
grok.templatedir("templates")


class AccountCreatedNotification(grok.View):
    grok.context(IUser)
    grok.name("account_created_notification")
    grok.template("mail_activate_account")

    def __init__(self, context, request):
        super(AccountCreatedNotification, self).__init__(context, request)
        user = api.portal.get_tool("acl_users").getUser(context.login)
        prt = api.portal.get_tool("portal_password_reset")
        reset = prt.requestReset(user.getId())
        self.reset_url="%s/@@reset-password/%s" % (
            api.portal.get().absolute_url(),
            reset["randomstring"]
        )


@grok.subscribe(IUser, IObjectAddedEvent)
def OnUserCreation(user, event):
    EmailActivationLink(user, event)


def NotifyError(user, e):
    log.error("MailHost error sending account activation link to: %s",
            user.contact_email, e)
    flash = IStatusMessage(user.REQUEST).addStatusMessage
    flash(_(u"error_activationmail",
            u'Could not send an account activation email to "%s".'
            u'Please contact the site administrator.'
        ), "error")
    return


def EmailActivationLink(user, event):
    registration = api.portal.get_tool('portal_registration')
    if not registration.isValidEmail(user.contact_email):
        return
    portal = api.portal.get()
    mailview = component.getMultiAdapter(
        (user, user.REQUEST),
        name="account_created_notification"
    )
    subject = _(u"password_reset_subject",
                default = u"Password reset for ${site}",
                mapping={'site':portal.title})
    email = createEmailTo(
        portal.email_from_name,
        portal.email_from_address,
        None,
        user.contact_email,
        translate(subject, context=user.REQUEST),
        mailview()
    )
    try:
        api.portal.get_tool('MailHost').send(email)
    except MailHostError, e:
        return NotifyError(e)
    except socket.error, e:
        return NotifyError(e[1])
    IStatusMessage(user.REQUEST).add(
        _("info_activation_mail_sent",
        default = u"An account activation email has been sent to the user."),
        "success")
    user.REQUEST.response.redirect(portal.absolute_url())


class PasswordValidator(user.PasswordValidator):
    grok.implements(IValidator)
    grok.adapts(
            Interface, IOSHAContentSkinLayer,
            IForm, schema.Password, IPasswordConfirmationWidget)

    def validate(self, value):
        if IAddForm.providedBy(self.view) and \
                self.view.portal_type in \
                    ['euphorie.countrymanager', 'euphorie.sector']:
            return
        return super(PasswordValidator, self).validate(value)
