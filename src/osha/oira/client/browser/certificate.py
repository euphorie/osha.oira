# coding=utf-8
from plone import api
from Products.Five import BrowserView
from plone.memoize.view import memoize


class Certificate(BrowserView):
    @property
    @memoize
    def webhelpers(self):
        return api.content.get_view("webhelpers", self.context, self.request)

    @property
    @memoize
    def country(self):
        """ The country inside /sectors that contains the certificates configuration
        """
        return api.portal.get().sectors[self.webhelpers.country]

    @property
    @memoize
    def completion_percentage(self):
        """ Report how much of the session the user has completed
        """
        return self.webhelpers.traversed_session.session.completion_percentage or 0

    def can_display_certificate_notice(self):
        """ Condition to show the certificate yellow box below the pie chart
        """
        country = self.country
        return (
            country.certificates_enabled
            and self.completion_percentage > country.certificate_initial_threshold
        )

    def can_display_certificate_teaser(self):
        """ Condition to show the invite for the user to earn the certificate
        """
        country = self.country
        return (
            country.certificates_enabled
            and country.certificate_initial_threshold
            <= self.completion_percentage
            < country.certificate_completion_threshold
        )

    def can_display_certificate_earned(self):
        """ Condition to show the link to the certificate view
        """
        country = self.country
        return (
            country.certificates_enabled
            and self.completion_percentage >= country.certificate_completion_threshold
        )

    @property
    @memoize
    def certificate(self):
        return {
            "title": self.request.form.get("title") or "DSakdsaj",
        }

    @property
    @memoize
    def site_title(self):
        """
        """
        return "Oira ciao"
