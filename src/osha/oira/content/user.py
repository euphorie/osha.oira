# coding=utf-8
from .. import _
from Acquisition import aq_parent
from Products.Archetypes.utils import IStatusMessage
from Products.MailHost.MailHost import MailHostError
from euphorie.content.sector import ISector
from euphorie.content import user
from euphorie.content.user import IUser
from five import grok
from os import urandom
from osha.oira.content.statistics import IOSHAContentSkinLayer
from p01.widget.password.interfaces import IPasswordConfirmationWidget
from plone import api
from plone.directives import form
from plonetheme.nuplone.utils import createEmailTo
from z3c.form.interfaces import IAddForm
from z3c.form.interfaces import IForm
from z3c.form.interfaces import IValidator
from zope import component
from zope import schema
from zope.i18n import translate
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IObjectAddedEvent
import logging
import socket
import string

log = logging.getLogger(__name__)
grok.templatedir("templates")


class AccountCreatedNotification(grok.View):
    grok.context(IUser)
    grok.name("account_created_notification")
    grok.template("mail_activate_account")

    def __init__(self, context, request):
        super(AccountCreatedNotification, self).__init__(context, request)
        user = api.portal.get_tool("acl_users").getUser(context.login)
        if ISector.providedBy(context):
            self.context_type = u"sector"
            self.context_title = context.Title()
            self.contact_name = context.contact_name
        else:
            self.context_type = u"country"
            self.context_title = aq_parent(context).Title()
            self.contact_name = context.Title()
        prt = api.portal.get_tool("portal_password_reset")
        reset = prt.requestReset(user.getId())
        self.reset_url = "%s/@@reset-password/%s" % (
            api.portal.get().absolute_url(),
            reset["randomstring"],
        )


@grok.subscribe(IUser, IObjectAddedEvent)
def OnUserCreation(user, event):
    if not user.contact_email:
        log.warn(
            u"Could not send activation email to user '%s',' no email set.",
            user.id,
        )
        return
    EmailActivationLink(user, event)


def NotifyError(user, e):
    log.error(
        "%r sending account activation link to: %s",
        e,
        user.contact_email,
    )
    flash = IStatusMessage(user.REQUEST).addStatusMessage
    flash(
        (
            u'Could not send an account activation email to "{}".'
            u'Please contact the site administrator.'
        ).format("error")
    )
    return


def EmailActivationLink(user, event):
    registration = api.portal.get_tool('portal_registration')
    if not registration.isValidEmail(user.contact_email):
        return
    portal = api.portal.get()
    mailview = component.getMultiAdapter(
        (user, user.REQUEST),
        name="account_created_notification",
    )
    subject = _(
        u"password_reset_subject",
        default=u"Password reset for ${site}",
        mapping={
            'site': portal.title,
        }
    )

    email = createEmailTo(
        api.portal.get_registry_record('plone.email_from_name'),
        api.portal.get_registry_record('plone.email_from_address'),
        None,
        user.contact_email,
        translate(subject, context=user.REQUEST),
        mailview(),
    )
    try:
        api.portal.get_tool('MailHost').send(email)
    except MailHostError as e:
        return NotifyError(user, e)
    except socket.error as e:
        return NotifyError(user, e[1])
    IStatusMessage(user.REQUEST).add(
        u"An account activation email has been sent to the user.", "success"
    )
    user.REQUEST.response.redirect(portal.absolute_url())


class PasswordValidator(user.PasswordValidator):
    grok.implements(IValidator)
    grok.adapts(
        Interface,
        IOSHAContentSkinLayer,
        IForm,
        schema.Password,
        IPasswordConfirmationWidget,
    )

    def validate(self, value):
        """ Don't validate when adding a country manager or sector.
            They'll get a default password (see default_password below) and
            then an email with link to set their password themselves.
            Refs: #10284
        """
        if (
            IAddForm.providedBy(self.view) and self.view.portal_type in [
                'euphorie.countrymanager',
                'euphorie.sector',
            ]
        ):
            return
        return super(PasswordValidator, self).validate(value)


@form.default_value(field=IUser['password'])
def default_password(data):
    """ Set a default value for passwords, otherwise new country managers and
        sectors will get empty passwords set.
        Refs: #10284
    """
    chars = string.letters + string.digits
    return u"".join([chars[ord(c) % len(chars)] for c in urandom(20)])
