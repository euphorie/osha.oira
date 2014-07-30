from Products.Archetypes.utils import IStatusMessage
from Products.MailHost.MailHost import MailHostError
from euphorie.content.countrymanager import ICountryManager
from zope import component
from five import grok
from plone import api
from plonetheme.nuplone.utils import createEmailTo
from zope.i18n import translate
from zope.lifecycleevent.interfaces import IObjectAddedEvent
import logging
import socket
from .. import _

log = logging.getLogger(__name__)
grok.templatedir("templates")


class AccountCreatedNotification(grok.View):
    grok.context(ICountryManager)
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


@grok.subscribe(ICountryManager, IObjectAddedEvent)
def OnCountryManagerCreation(manager, event):
    EmailActivationLink(manager, event)


def NotifyError(manager, e):
    log.error("MailHost error sending account activation link to: %s",
            manager.contact_email, e)
    flash = IStatusMessage(manager.REQUEST).addStatusMessage
    flash(_(u"error_activationmail",
            u'Could not send an account activation email to "%s".'
            u'Please contact the site administrator.'
        ), "error")
    return


def EmailActivationLink(manager, event):
    registration = api.portal.get_tool('portal_registration')
    if not registration.isValidEmail(manager.contact_email):
        return
    portal = api.portal.get()
    mailview = component.getMultiAdapter(
        (manager, manager.REQUEST),
        name="account_created_notification"
    )
    subject = _(u"password_reset_subject",
                default = u"Password reset for ${site}",
                mapping={'site':portal.title})
    email = createEmailTo(
        portal.email_from_name,
        portal.email_from_address,
        None,
        manager.contact_email,
        translate(subject, context=manager.REQUEST),
        mailview()
    )
    try:
        api.portal.get_tool('MailHost').send(email)
    except MailHostError, e:
        return NotifyError(e)
    except socket.error, e:
        return NotifyError(e[1])
    IStatusMessage(manager.REQUEST).add(
        _("info_activation_mail_sent",
        default = u"An account activation email has been sent to the user."),
        "success")
    manager.REQUEST.response.redirect(portal.absolute_url())
