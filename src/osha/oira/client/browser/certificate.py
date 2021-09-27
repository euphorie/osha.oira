# coding=utf-8
from euphorie.client import utils
from euphorie.content.utils import getRegionTitle
from osha.oira.client import model
from plone import api
from plone.memoize.view import memoize
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from z3c.saconfig import Session
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import json
import uuid


class Certificate(BrowserView):
    @property
    @memoize
    def webhelpers(self):
        return api.content.get_view("webhelpers", self.context, self.request)

    @property
    @memoize
    def public_server_url(self):
        return api.portal.get_registry_record("osha.oira.certificate.public_server")

    @property
    @memoize
    def country_adapter(self):
        """Try to get a specific adapter for this country
        that will be used to show and handle additional fields in the certificate

        The adapter should be a view like @@certificate_fr_specific
        """
        try:
            return api.content.get_view(
                "certificate_%s_specific" % self.webhelpers.country,
                self.context,
                self.request,
            )
        except api.exc.InvalidParameterError:
            pass

    @property
    @memoize
    def known_field_names(self):
        """Return the field names we expect to have in the form

        By default we expect to have a title
        """
        return ("title", "company_identification_number") + getattr(
            self.country_adapter, "extra_known_field_names", ()
        )

    @property
    @memoize
    def site_title(self):
        return api.portal.get_registry_record("plone.site_title")

    @property
    @memoize
    def country(self):
        """The country inside /sectors that contains the certificates configuration"""
        return api.portal.get().sectors[self.webhelpers.country]

    @property
    @memoize
    def language(self):
        return self.webhelpers._survey.language

    @property
    @memoize
    def completion_percentage(self):
        """Report how much of the session the user has completed"""
        return self.webhelpers.traversed_session.session.completion_percentage or 0

    def can_display_certificate_notice(self):
        """Condition to show the certificate yellow box below the pie chart"""
        country = self.country
        return (
            getattr(country, "certificates_enabled", False)
            and self.completion_percentage >= country.certificate_initial_threshold
        )

    def can_display_certificate_teaser(self):
        """Condition to show the invite for the user to earn the certificate"""
        country = self.country
        return (
            getattr(country, "certificates_enabled", False)
            and country.certificate_initial_threshold
            <= self.completion_percentage
            < country.certificate_completion_threshold
        )

    def can_display_certificate_earned(self):
        """Condition to show the link to the certificate view"""
        country = self.country
        return (
            getattr(country, "certificates_enabled", False)
            and self.completion_percentage >= country.certificate_completion_threshold
        )

    @property
    @memoize
    def certificate(self):
        """Find the certificate associated to this session"""
        return (
            Session.query(model.Certificate)
            .filter(model.Certificate.session_id == self.webhelpers.session_id)
            .one()
        )

    @property
    @memoize
    def session(self):
        return self.webhelpers.traversed_session.session

    @property
    def session_url(self):
        return self.webhelpers.traversed_session.absolute_url()

    @property
    def tool_name(self):
        return self.webhelpers.tool_name

    @property
    def country_name(self):
        return getRegionTitle(self.request, self.session.country.upper())

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
        values = self.certificate_json
        new_values = {
            key: self.request.form.get(key)
            for key in self.known_field_names
            if key in self.request.form
        }

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


@implementer(IPublishTraverse)
class PublicCertificate(BrowserView):
    """View to publish a public certificate once the hash is known"""

    def publishTraverse(self, request, name):
        self.secret = name
        return self

    @property
    def certificate(self):
        if not getattr(self, "secret", None):
            return None
        query = Session.query(model.Certificate).filter(
            model.Certificate.secret == safe_unicode(self.secret)
        )
        if query.count():
            return query.one()

    @property
    @memoize
    def session(self):
        """Find the certificate associated to this session"""
        return self.certificate.session

    @property
    @memoize
    def survey(self):
        try:
            return self.context.restrictedTraverse(str(self.session.zodb_path))
        except Exception:
            return None

    @property
    def tool_name(self):
        return self.survey.Title() if self.survey else ""

    @property
    def country_name(self):
        return getRegionTitle(self.request, self.session.country.upper())

    @property
    @memoize
    def language(self):
        if self.survey:
            return self.survey.language
        return "en"

    @property
    @memoize
    def certificate_json(self):
        try:
            return json.loads(self.certificate.json)
        except (TypeError, ValueError):
            return {}

    @property
    @memoize
    def country_adapter(self):
        """Try to get a specific adapter for this country
        that will be used to show and handle additional fields in the certificate

        The adapter should be a view like @@certificate_fr_specific
        """
        try:
            return api.content.get_view(
                "certificate_%s_specific" % self.session.zodb_path.partition("/")[0],
                self.context,
                self.request,
            )
        except api.exc.InvalidParameterError:
            pass

    def __call__(self):
        utils.setLanguage(self.request, self.context, self.language)
        return super(PublicCertificate, self).__call__()


class RemoveCertificateBox(BrowserView):
    @property
    @memoize
    def webhelpers(self):
        return api.content.get_view("webhelpers", self.context, self.request)

    def maybe_update(self):
        if self.request.method != "POST":
            return

        if not self.webhelpers.show_certificate_status_box():
            # Already added
            return

        Session.add(
            model.UsersNotInterestedInCertificateStatusBox(
                account_id=self.webhelpers.get_current_account().id
            )
        )

    def __call__(self):
        self.maybe_update()
        # Redirect to Report, since this is a cheap view, to get the main navigation
        self.request.RESPONSE.redirect(
            "{session}/@@report".format(session=self.context.absolute_url())
        )
