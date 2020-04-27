# coding=utf-8
from osha.oira.client import model
from plone import api
from plone.memoize.view import memoize
from Products.Five import BrowserView
from z3c.saconfig import Session

import json
import uuid


class Certificate(BrowserView):
    @property
    @memoize
    def webhelpers(self):
        return api.content.get_view("webhelpers", self.context, self.request)

    @property
    @memoize
    def site_title(self):
        return api.portal.get_registry_record("plone.site_title")

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
        """ Find the certificate associated to this session
        """
        return (
            Session.query(model.Certificate)
            .filter(model.Certificate.session_id == self.webhelpers.session_id)
            .one()
        )

    @property
    @memoize
    def certificate_json(self):
        try:
            return json.loads(self.certificate.json)
        except (TypeError, ValueError):
            return {}

    def maybe_update(self):
        if self.request.method != "POST":
            return
        known_keys = (
            "title",
        )
        values = self.certificate_json
        new_values = {key: self.request.form.get(key) for key in known_keys if key in self.request.form}

        if self.request.form.get("public"):
            self.certificate.secret = uuid.uuid4().hex
        else:
            self.certificate.secret = None

        if new_values == {key: self.certificate_json.get(key) for key in new_values}:
            return

        values.update(new_values)
        self.certificate.json = json.dumps(values)


    def __call__(self):
        self.maybe_update()
        return super(Certificate, self).__call__()
