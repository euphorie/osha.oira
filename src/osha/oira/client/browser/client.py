# coding=utf-8
from euphorie.client.model import Account
from json import dumps
from os import path
from osha.oira.client.model import NewsletterSubscription
from plone import api
from Products.Five import BrowserView
from z3c.saconfig import Session
from zExceptions import Unauthorized


class MailingListsJson(BrowserView):
    """Mailing lists (countries, in the future also sectors and tools)"""

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
        all_users = {"id": "general", "text": "All users"}
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
                {"id": path.relpath(brain.getPath(), client_path), "text": brain.Title}
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
        return dumps(self.results)


class GroupToAddresses(BrowserView):
    """Resolve email addresses subscribed to the given mailing list."""

    def get_token(self):
        token = api.portal.get_registry_record("osha.oira.mailings.token")
        if not token:
            raise Unauthorized("Invalid token")
        return token

    def get_addresses_for_group(self, group_path):
        subscribers = (
            Session.query(Account.loginname)
            .filter(Account.id == NewsletterSubscription.account_id)
            .filter(NewsletterSubscription.zodb_path == group_path)
        )
        return [s.loginname for s in subscribers]

    @property
    def results(self):
        group_path = self.request.get("group", "")
        if not group_path:
            return []
        return self.get_addresses_for_group(group_path)

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