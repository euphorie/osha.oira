from euphorie.client.country import IClientCountry
from euphorie.client.model import get_current_account
from osha.oira import _
from osha.oira.client.model import NewsletterSetting
from plone import api
from plone.memoize.view import memoize
from Products.Five import BrowserView
from z3c.saconfig import Session


class View(BrowserView):
    """View for the dashboard banner."""

    @property
    @memoize
    def webhelpers(self):
        return api.content.get_view("webhelpers", self.context, self.request)

    @property
    @memoize
    def all_messages(self):
        country_url = self.webhelpers.country_url
        help_language = self.webhelpers.help_language
        link_text = api.portal.translate(_("personal preferences page"))
        preferences_link = (
            f'<a class="pat-inject" href="{self.preferences_url}">{link_text}</a>.'
        )
        return [
            {
                "img_src": "++resource++euphorie.resources/oira/style/mail-tunnel.jpg",
                "img_alt": api.portal.translate(_("Preferences")),
                "url": self.preferences_url,
                "button_text": api.portal.translate(_("Sign up")),
                "text": api.portal.translate(
                    _(
                        "Keep updated with the latest developments by signing up for "
                        "our newsletter on your ${target}.",
                        mapping={"target": preferences_link},
                    )
                ),
                "data_pat_inject": (
                    "source: #content; target: #content; history: record"
                ),
                "disabled_key": "call-for-action-banner-disabled",
            },
            {
                "img_src": (
                    "++resource++euphorie.resources/oira/style/"
                    "andrea-piacquadio-copier.jpg"
                ),
                "img_alt": api.portal.translate(_("Photocopier")),
                "url": (
                    f"{country_url}/++resource++euphorie.resources/oira/help/"
                    f"{help_language}/pages/3-carrying-out-a-risk-assessment.html"
                ),
                "button_text": api.portal.translate(_("Learn more…")),
                "text": api.portal.translate(
                    _(
                        "Tip: Re-use existing risk assessments with the duplication "
                        "feature."
                    )
                ),
                "data_pat_inject": (
                    "source: #content; target: #content; "
                    "history: record; scroll: #duplication"
                ),
                "disabled_key": "duplication-banner-disabled",
            },
        ]

    @property
    @memoize
    def messages(self):
        account = get_current_account()
        if not account:
            return []

        hidden_keys = [
            message.value
            for message in Session.query(NewsletterSetting.value).filter(
                NewsletterSetting.account_id == account.id,
                NewsletterSetting.value.in_(
                    [message["disabled_key"] for message in self.all_messages]
                ),
            )
        ]
        return [
            message
            for message in self.all_messages
            if message["disabled_key"] not in hidden_keys
        ]

    @property
    def message_id(self):
        return int(self.request.form.get("message", 0))

    @property
    def message(self):
        return self.messages[self.message_id]

    @property
    def preferences_url(self):
        for obj in self.context.aq_chain:
            if IClientCountry.providedBy(obj):
                return f"{obj.absolute_url()}/@@preferences#content"
        return ""

    def available(self):
        """Check if the user already closed the banner in the past."""
        return self.messages

    def __call__(self):
        if (
            self.request.method == "POST"
            and self.request.form.get("hide_banner") == "1"
        ):
            value = self.request.form.get("value")
            if value in [message["disabled_key"] for message in self.all_messages]:
                Session.add(
                    NewsletterSetting(
                        account_id=get_current_account().getId(),
                        value=value,
                    )
                )
            self.request.response.redirect(self.context.absolute_url())
        return super().__call__()
