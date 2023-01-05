from euphorie.client.model import get_current_account
from osha.oira.client.model import NewsletterSetting
from Products.Five import BrowserView
from z3c.saconfig import Session


class View(BrowserView):
    """View for the dashboard banner."""

    _value = "call-for-action-banner-disabled"

    def available(self):
        """Check if the user already closed the banner in the past."""
        account = get_current_account()
        if not account:
            return False
        return (
            Session.query(NewsletterSetting)
            .filter(
                NewsletterSetting.account_id == account.id,
                NewsletterSetting.value == self._value,
            )
            .count()
            == 0
        )

    def __call__(self):
        if (
            self.request.method == "POST"
            and self.request.form.get("hide_banner") == "1"
        ):
            Session.add(
                NewsletterSetting(
                    account_id=get_current_account().getId(),
                    value=self._value,
                )
            )
            self.request.response.redirect(self.context.absolute_url())
        return super().__call__()
