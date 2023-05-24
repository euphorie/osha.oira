from euphorie import MessageFactory as _
from euphorie.client.browser.session import Start
from logging import getLogger
from osha.oira.client.interfaces import IOSHAClientSkinLayer
from osha.oira.client.model import NewsletterSubscription
from plone import api
from plone.memoize.view import memoize
from plone.z3cform.fieldsets.extensible import FormExtender
from plone.z3cform.fieldsets.interfaces import IFormExtender
from sqlalchemy import sql
from z3c.form.field import Fields
from z3c.saconfig import Session
from zope import schema
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


logger = getLogger(__name__)


class IOSHAStartExtender(Interface):
    """Add a some fields, ie.

    a checkbox that allows to subscribe to the newsletter
    """

    tool_subscription = schema.Bool(
        title=_(
            "label_tool_subscription",
            # XXX
            # default="Send me occasional e-mails with news about the tool 'Tool name'",
            default="Send me occasional e-mails with news about this tool",
        ),
        required=False,
        default=True,
    )


@implementer(IFormExtender)
@adapter(Interface, IOSHAClientSkinLayer, Start)
class OSHAStartExtender(FormExtender):
    fields = Fields(IOSHAStartExtender)

    @property
    @memoize
    def webhelpers(self):
        return api.content.get_view("webhelpers", self.context, self.request)

    @memoize
    def update(self):
        """Omit the group id field if we are not the creator."""
        if self.webhelpers.can_edit_session:
            self.add(self.fields)


class OSHAStart(Start):
    def get_tool_subscriptions(self):
        """In principle we can have multiple rows.

        Normally it is 0 or 1.
        """
        account = self.webhelpers.get_current_account()
        return Session.query(NewsletterSubscription).filter(
            sql.and_(
                NewsletterSubscription.account_id == account.id,
                NewsletterSubscription.zodb_path == self.context.session.zodb_path,
            )
        )

    def is_tool_subscription_enabled(self):
        return self.get_tool_subscriptions().count() > 0

    def set_tool_subscription(self, value):
        """Check if we need to save or delete the subscription from the tool
        bound to the current session."""
        if value:
            if not self.is_tool_subscription_enabled():
                account = self.webhelpers.get_current_account()
                Session.add(
                    NewsletterSubscription(
                        account_id=account.id,
                        zodb_path=self.context.session.zodb_path,
                    )
                )
        else:
            for subscription in self.get_tool_subscriptions():
                Session.delete(subscription)

    def updateWidgets(self):
        super().updateWidgets()
        if "tool_subscription" in self.widgets:
            if not self.is_tool_subscription_enabled():
                self.widgets["tool_subscription"].value = []

    def _set_data(self, data):
        tool_subscription = bool(data.pop("tool_subscription", None))
        self.set_tool_subscription(tool_subscription)
        super()._set_data(data)
