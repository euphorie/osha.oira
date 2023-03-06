from euphorie.client.browser.settings import Preferences
from euphorie.client.model import get_current_account
from osha.oira import _
from osha.oira.client.model import NewsletterSubscription
from plone import api
from plone.memoize.view import memoize
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import button
from z3c.saconfig import Session


class OSHAPreferences(Preferences):
    """"""

    template = ViewPageTemplateFile("templates/preferences.pt")

    @property
    @memoize
    def webhelpers(self):
        return api.content.get_view("webhelpers", self.context, self.request)

    @property
    @memoize
    def my_sessions(self):
        return self.webhelpers.get_sessions_query(
            context=self.webhelpers.client,
            include_archived=True,
            filter_by_account=True,
        )

    @property
    @memoize
    def my_countries(self):
        return {s.country for s in self.my_sessions}

    @property
    @memoize
    def my_sectors(self):
        # TODO
        return set()

    @property
    @memoize
    def my_tools(self):
        return {s.zodb_path for s in self.my_sessions}

    @property
    @memoize
    def existing_subscriptions(self):
        existing_subscriptions = Session.query(NewsletterSubscription).filter(
            NewsletterSubscription.account_id == get_current_account().getId()
        )
        return {
            subscription.zodb_path: subscription
            for subscription in existing_subscriptions
        }

    @property
    def has_general_subscription(self):
        return self.existing_subscriptions.get("general")

    @property
    def has_country_subscription(self):
        # TODO: User could have multiple countries, but there's only one checkbox
        # If I have two countries but am only subscribed to one of them, then
        # this will say I am subscribed to my country. However, saving the form will add
        # a subscription to the other country, even though I haven't changed anything.
        return any(
            self.existing_subscriptions.get(country) for country in self.my_countries
        )

    def subscribe(self, zodb_path):
        if zodb_path not in self.existing_subscriptions:
            Session.add(
                NewsletterSubscription(
                    account_id=get_current_account().getId(),
                    zodb_path=zodb_path,
                )
            )

    def unsubscribe(self, zodb_path):
        if zodb_path in self.existing_subscriptions:
            Session.delete(self.existing_subscriptions[zodb_path])

    @button.buttonAndHandler(_("Save"), name="save")
    def handleSave(self, action):
        super().handleSave(self, action)
        mailings = self.request.get("mailings", {})

        wants_general_subscription = mailings.get("general", False)
        if wants_general_subscription:
            self.subscribe("general")
        else:
            self.unsubscribe("general")

        wants_country_subscription = mailings.get("country", False)
        if wants_country_subscription:
            for country_id in self.my_countries:
                self.subscribe(country_id)
        else:
            for country_id in self.my_countries:
                self.unsubscribe(country_id)

        for tool_id in self.my_tools:
            if tool_id in mailings:
                self.subscribe(tool_id)
            else:
                self.unsubscribe(tool_id)
        # TODO: Remove subscriptions for deleted assessments

        self.request.__annotations__.pop("plone.memoize", None)
