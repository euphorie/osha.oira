from base64 import b64encode
from euphorie.client.model import Account
from euphorie.client.model import SurveySession
from euphorie.content.country import ICountry
from json import dumps
from json import JSONDecodeError
from json import loads
from os import path
from osha.oira import _
from osha.oira.client.interfaces import IOSHAClientSkinLayer
from osha.oira.client.model import NewsletterSetting
from osha.oira.client.model import NewsletterSubscription
from plone import api
from plone.memoize.view import memoize
from plone.scale.scale import scaleImage
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.saconfig import Session
from zExceptions import Unauthorized
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces import IPublishTraverse

import hashlib


_marker = object()


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


class BaseJson(BrowserView):
    """Base for Quaive/OiRA json interface"""

    def _get_entry(self, list_id, title):
        encoded_title = b64encode(title.encode("utf-8")).decode("utf-8")
        return {
            "id": "|".join((list_id, encoded_title)),
            "text": title,
        }

    def validate_ticket(self):
        """Authenticate the user specified by request parameters `user_id` and
        `ticket`"""
        user_id = self.request.get("user_id")
        if not user_id:
            raise Unauthorized("Invalid user_id")
        ticket = self.request.get("ticket")
        if not ticket:
            raise Unauthorized("Invalid ticket")

        token = api.portal.get_registry_record("osha.oira.mailings.token", default="")

        payload = "|".join([user_id, token])
        expected = hashlib.blake2b(payload.encode()).hexdigest()

        if ticket != expected:
            raise Unauthorized("Invalid ticket")

    def __call__(self):
        """Returns a json meant to be consumed by pat-autosuggest.

        The json lists container that will be used to generate "mailing
        lists"
        """
        self.validate_ticket()
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader("Access-Control-Allow-Origin", "*")
        return dumps(self.results)


class MailingListsJson(BaseJson):
    """Mailing lists (countries and tools, in the future also sectors)"""

    @property
    @memoize
    def addresses_view(self):
        return api.content.get_view(
            context=self.context, request=self.request, name="group-to-addresses"
        )

    def _get_entry(self, list_id, title):
        encoded_title = b64encode(title.encode("utf-8")).decode("utf-8")
        num_subscribers = len(self.addresses_view.get_addresses_for_groups([list_id]))
        path_or_nothing = f" ({list_id})" if "/" in list_id else ""
        return {
            "id": "|".join((list_id, encoded_title)),
            "text": f"{title}{path_or_nothing} [{num_subscribers} subscribers]",
        }

    @property
    @memoize
    def client_path(self):
        return "/".join(self.context.getPhysicalPath())

    def _get_mailing_lists_for(self, brain):
        if brain.portal_type != "euphorie.clientcountry":
            return [
                self._get_entry(
                    path.relpath(brain.getPath(), self.client_path), brain.Title
                )
            ]
        languages = set()
        tools = api.content.find(
            path=brain.getPath(),
            portal_type="euphorie.survey",
        )
        # No filter for non-obsolete -
        # if we get unexpected languages we can try adding that
        for tool in tools:
            language = tool.Language
            if language:
                if "-" in language:
                    language = language.split("-")[0]
                if language and language != "None":
                    languages.add(language)

        return [
            self._get_entry(
                "-".join((brain.getId, language)), f"{brain.Title} ({language})"
            )
            for language in languages
        ]

    @property
    def results(self):
        """List of "mailing list" path/names.

        The format fits pat-autosuggest.

        The mailing list IDs are relative paths.
        Countries have one mailing list per language.
        The language is appended with a '-', e.g. "be-fr".
        There is a special ID for the "all users" list.
        """
        user_id = self.request.get("user_id")

        q = self.request.get("q", "").strip().lower()

        results = []
        catalog = api.portal.get_tool(name="portal_catalog")
        all_users = self._get_entry("general", "All users")

        # Make sure we don't get a client user - we want to check backend permissions
        noLongerProvides(self.request, IOSHAClientSkinLayer)

        with api.env.adopt_user(user_id):
            print(api.user.get_current().getUserId())

            if (
                not q or q in all_users["id"] or q in all_users["text"].lower()
            ) and api.user.has_permission("Manage portal content"):
                results.append(all_users)

            # FIXME: Search for native names of countries,
            # e.g. `q=de` doesn't return Germany
            # TODO: also search for "euphorie.clientsector"?
            query = {
                "portal_type": ["euphorie.clientcountry", "euphorie.survey"],
                "path": "/".join(self.context.getPhysicalPath()),
                "sort_on": "sortable_title",
            }

            # Filter for query string if given. Else return all results.
            if q:
                if "/" not in q:
                    query["Title"] = f"*{q}*"
                else:
                    query["path"] = "/".join((query["path"], q))

            brains = catalog(**query)

            sectors = api.portal.get().sectors

            def filter_items(brain):
                obj = brain.getObject()

                if getattr(obj, "preview", False) or getattr(obj, "obsolete", False):
                    return False

                counterpart = sectors.restrictedTraverse(
                    brain.getPath().split("/")[3:], None
                )
                if not counterpart:
                    return False

                if api.user.has_permission("Euphorie: Manage country", obj=counterpart):
                    return True

                return {"Manager", "Sector", "CountryManager"} & set(
                    api.user.get_roles(obj=counterpart)
                )

            filtered_brains = filter(filter_items, brains)

            for brain in filtered_brains:
                results.extend(self._get_mailing_lists_for(brain))

        return results


class LogosJson(BaseJson):
    @property
    def results(self):
        """List of country logo URLs and country names.

        The format fits pat-autosuggest.
        """
        user_id = self.request.get("user_id")
        user = api.user.get(username=user_id)
        sectors = api.portal.get().sectors
        results = []
        client_folder = api.portal.get().client
        for country in sectors.objectValues():
            if (
                ICountry.providedBy(country)
                and api.user.has_permission(
                    "Euphorie: Manage country", user=user, obj=country
                )
                and country.image
                and country.id in client_folder
            ):
                client_country = client_folder[country.id]
                url = f"{client_country.absolute_url()}/@@mail_header_image/{country.image.filename}"  # noqa: E501
                results.append(self._get_entry(url, country.title))
        return results


@implementer(IPublishTraverse)
class MailHeaderImage(BrowserView):
    def publishTraverse(self, request, name):
        # URL looks like /eu/filename.jpg
        # The first time we enter here name is "eu" and we want to record it
        # in self._country.
        # The following times we are not interested in the name anymore
        if getattr(self, "country", _marker) is _marker:
            self._country = name
        return self

    @property
    def country(self):
        return api.portal.get().sectors[self.context.id]

    @property
    def scaled_image(self):
        """Return the scaled image"""
        image = self.country.image
        width, height = image.getImageSize()
        ratio = width / height
        return scaleImage(image.data, width=int(100 * ratio), height=100)[0]

    def __call__(self):
        """
        Take the image field and scale it to 100px using PIL
        """
        data = self.scaled_image
        self.request.response.setHeader("Content-type", self.country.image.contentType)
        self.request.response.setHeader("Content-length", len(data))
        return data


class GroupToAddresses(BrowserView):
    """Resolve email addresses subscribed to the given mailing list."""

    def get_token(self):
        token = api.portal.get_registry_record("osha.oira.mailings.token")
        if not token:
            raise Unauthorized("Invalid token")
        return token

    def get_addresses_for_groups(self, group_paths):
        subscribers = []
        other = []
        for group_id in group_paths:
            if "/" in group_id or "-" not in group_id:
                other.append(group_id)
                continue
            # Special handling for language specific mailing lists, e.g. "be-fr"
            country, lang = group_id.split("-")
            country_subscribers = (
                Session.query(Account.loginname)
                .filter(Account.id == NewsletterSubscription.account_id)
                .filter(NewsletterSubscription.zodb_path == (country))
                .filter(Account.id == NewsletterSetting.account_id)
                .filter(NewsletterSetting.value == f"language:{lang}")
                .group_by(Account.loginname)
            )
            subscribers.extend([s.loginname for s in country_subscribers])

        other_subscribers = (
            Session.query(Account.loginname)
            .filter(Account.id == NewsletterSubscription.account_id)
            .filter(NewsletterSubscription.zodb_path.in_(other))
            .group_by(Account.loginname)
        )
        subscribers.extend([s.loginname for s in other_subscribers])
        return subscribers

    @property
    def results(self):
        groups = self.request.get("groups", "")
        if not groups:
            return []
        return self.get_addresses_for_groups(groups.split(","))

    def __call__(self):
        """Json list of email addresses subscribed to given group path
        (parameter `group`).

        Group paths are relative to the client, e.g. "be/agriculture/agriculture".
        For countries the ID is combined with a language, e.g. "be-fr".
        See also `MailingListsJson`
        """
        token = self.request.get("token", "")
        if token != self.get_token():
            raise Unauthorized("Invalid token")

        self.request.response.setHeader("Content-type", "application/json")
        return dumps(self.results)


class RecipientLanguageMapping(BrowserView):
    @property
    def results(self):
        recipients = self.request.get("recipients", [])
        if recipients and isinstance(recipients, str):
            try:
                recipients = loads(recipients)
            except (TypeError, JSONDecodeError):
                recipients = [recipients]
        if not recipients:
            return {}
        query = (
            Session.query(Account.loginname, SurveySession.zodb_path)
            .join(SurveySession, Account.id == SurveySession.account_id)
            .filter(Account.loginname.in_(recipients))
            .distinct()
        )

        default_language = api.portal.get_default_language()

        def get_country_and_language(zodb_path):
            country = zodb_path.partition("/")[0]
            # XXX Language should come from user preferences in the future
            language = country if country != "eu" else default_language
            return {"country": country, "language": language}

        return {
            account: get_country_and_language(zodb_path) for account, zodb_path in query
        }

    def get_token(self):
        token = api.portal.get_registry_record("osha.oira.mailings.token")
        if not token:
            raise Unauthorized("Invalid token")
        return token

    def __call__(self):
        token = self.request.get("token", "")
        if token != self.get_token():
            raise Unauthorized("Invalid token")

        self.request.response.setHeader("Content-type", "application/json")
        return dumps(self.results)


class NewsletterUnsubscribe(BrowserView):
    """Unsubscribe a user from a mailing list.

    This should work without logging in, i.e. via an authentication
    token.
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

        message = "|".join((email, group or "*", self.get_token()))
        digest = hashlib.sha256(message.encode()).hexdigest()
        if digest == token:
            self.unsubscribe(email, group)
            self.success = True
        return self.index()
