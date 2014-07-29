from Products.CMFPlone.RegistrationTool import SMTPRecipientsRefused
from plone import api
from zope import component
from zope.lifecycleevent.interfaces import IObjectAddedEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from five import grok
from euphorie.content.countrymanager import ICountryManager
import logging
from .. import _

log = logging.getLogger(__name__)
grok.templatedir("templates")


class AccountCreatedNotification(grok.View):
    grok.context(ICountryManager)
    grok.name("account_created_notification")
    grok.template("mail_country_manager_account_created")
    

@grok.subscribe(ICountryManager, IObjectAddedEvent)
def OnAdded(manager, event):
    NotifyCountryManager(manager, event)


@grok.subscribe(ICountryManager, IObjectModifiedEvent)
def OnModified(manager, event):
    NotifyCountryManager(manager, event)


def NotifyCountryManager(manager, event):
    mailhost = api.portal.get_tool('MailHost')
    pm = api.portal.get_tool('portal_membership')
    recipient = manager.contact_email
    mailview = component.getMultiAdapter(
        (manager, manager.REQUEST),
        name="account_created_notification"
    )
    try:
        mailhost.send(
            mailview(),
            mto=recipient,
            mfrom=api.portal.get().getProperty('email_from_address'),
            subject=_('Your OiRA account has been created'),
            immediate=True,
            charset='utf-8',
            msg_type='text/html'
        )
    except SMTPRecipientsRefused, e:
        log.error(e)
