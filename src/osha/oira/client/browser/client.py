from base64 import b64encode
from euphorie.client.model import Account
from json import dumps
from os import path
from osha.oira import _
from osha.oira.client.model import NewsletterSubscription
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.saconfig import Session
from zExceptions import Unauthorized

import hashlib
import re


class OSHAClientRedirect(BrowserView):
    def __call__(self):
        # XXX get the user's country instead of the default one
        # so that they see their assessments
        country = (
            api.portal.get_registry_record("euphorie.default_country", default="")
            or "eu"
        )
        return self.request.response.redirect(
            f"{self.context.absolute_url()}/{country}/@@{self.__name__}?"
            f"{self.request.get('QUERY_STRING')}"
        )


class MailingListsJson(BrowserView):
    """Mailing lists (countries, in the future also sectors and tools)"""

    def _get_entry(self, list_id, title):
        encoded_title = b64encode(title.encode("utf-8")).decode("utf-8")
        return {
            "id": "|".join((list_id, encoded_title)),
            "text": title,
        }

    @property
    def results(self):
        """List of "mailing list" path/names.

        The format fits pat-autosuggest. There is a special label for
        the "all" list.
        """
        q = self.request.get("q", "").strip().lower()
        if not q:
            return []

        results = []
        catalog = api.portal.get_tool(name="portal_catalog")
        all_users = self._get_entry("general", "All users")
        if q in all_users["id"] or q in all_users["text"].lower():
            results.append(all_users)

        # FIXME: Search for native names of countries,
        # e.g. `q=de` doesn't return Germany
        brains = catalog(
            portal_type=["euphorie.clientcountry", "euphorie.survey"],
            Title=f"*{q}*",
            path="/".join(self.context.getPhysicalPath()),
            sort_on="sortable_title",
        )
        client_path = "/".join(self.context.getPhysicalPath())
        results.extend(
            [
                self._get_entry(path.relpath(brain.getPath(), client_path), brain.Title)
                for brain in brains
            ]
        )
        return results

    def __call__(self):
        """Returns a json meant to be consumed by pat-autosuggest.

        The json lists container that will be used to generate "mailing
        lists"
        """
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader("Access-Control-Allow-Origin", "*")
        return dumps(self.results)


class GroupToAddresses(BrowserView):
    """Resolve email addresses subscribed to the given mailing list."""

    def get_token(self):
        token = api.portal.get_registry_record("osha.oira.mailings.token")
        if not token:
            raise Unauthorized("Invalid token")
        return token

    def get_addresses_for_groups(self, group_paths):
        subscribers = (
            Session.query(Account.loginname)
            .filter(Account.id == NewsletterSubscription.account_id)
            .filter(NewsletterSubscription.zodb_path.in_(group_paths))
            .group_by(Account.loginname)
        )
        return [s.loginname for s in subscribers]

    @property
    def results(self):
        groups = self.request.get("groups", "")
        if not groups:
            return []
        return self.get_addresses_for_groups(groups.split(","))

    def __call__(self):
        """Json list of email addresses subscribed to given group path
        (parameter `group`).

        Group paths are relative to the client, i.e. only ids ("fr") for
        countries.
        """
        token = self.request.get("token", "")
        if token != self.get_token():
            raise Unauthorized("Invalid token")

        self.request.response.setHeader("Content-type", "application/json")
        return dumps(self.results)


class NewsletterUnsubscribe(BrowserView):
    """Unsubscribe a user from a mailing list.

    This should work without logging in, i.e. via an authentication token.
    """

    index = ViewPageTemplateFile("templates/unsubscribe.pt")

    def get_token(self):
        token = api.portal.get_registry_record("osha.oira.mailings.token")
        if not token:
            raise Unauthorized("Invalid token")
        return token

    @property
    def group_title(self):
        group = self.request.form.get("group")
        if group == "general":
            return _("label_general_news", default="General OiRA News")
        group_obj = self.context.aq_parent.unrestrictedTraverse(group)
        return group_obj.title

    def unsubscribe(self, email, group):
        existing_subscriptions = (
            Session.query(NewsletterSubscription)
            .filter(Account.id == NewsletterSubscription.account_id)
            .filter(Account.loginname == email)
        )
        if group:
            existing_subscriptions = existing_subscriptions.filter(
                NewsletterSubscription.zodb_path == group
            )
        for subscription in existing_subscriptions:
            Session.delete(subscription)

    def __call__(self):
        email = self.request.form.get("email")
        group = self.request.form.get("group")
        token = self.request.form.get("token")

        self.success = False

        email_regex = re.compile(r"[A-Za-z0-9@.]*")
        if not email_regex.fullmatch(email):
            return self.index()
        group_regex = re.compile(r"[A-Za-z0-9/\-_]*")
        if group and not group_regex.fullmatch(group):
            return self.index()

        message = "|".join((email, group or "*", self.get_token()))
        digest = hashlib.sha256(message.encode()).hexdigest()
        if digest == token:
            self.unsubscribe(email, group)
            self.success = True
        return self.index()
