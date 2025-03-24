from datetime import date
from euphorie.client import utils
from euphorie.client.browser.certificate import Certificate
from euphorie.client.browser.certificate import CertificateOverview
from euphorie.content.utils import getRegionTitle
from osha.oira.client import model
from plone import api
from plone.memoize.view import memoize
from plone.protect.interfaces import IDisableCSRFProtection
from Products.Five import BrowserView
from z3c.saconfig import Session
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import json
import uuid


class OSHACertificate(Certificate):
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
        """Try to get a specific adapter for this country that will be used to
        show and handle additional fields in the certificate.

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
        """Return the field names we expect to have in the form.

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
        """The country inside /sectors that contains the certificates
        configuration."""
        return api.portal.get().sectors[self.webhelpers.country]

    @property
    @memoize
    def language(self):
        return self.webhelpers._survey.language

    @property
    @memoize
    def completion_percentage(self):
        """Report how much of the session the user has completed."""
        return self.webhelpers.traversed_session.session.completion_percentage or 0

    def can_display_certificate_notice(self):
        """Condition to show the certificate yellow box below the pie chart."""
        country = self.country
        return (
            getattr(country, "certificates_enabled", False)
            and self.completion_percentage >= country.certificate_initial_threshold
        )

    def can_display_certificate_teaser(self):
        """Condition to show the invite for the user to earn the
        certificate."""
        country = self.country
        return (
            getattr(country, "certificates_enabled", False)
            and country.certificate_initial_threshold
            <= self.completion_percentage
            < country.certificate_completion_threshold
        )

    def maybe_create_earned_certificate(self):
        """Check if certificates are enabled in this country and if the user
        has earned the certificate for this session.

        In case the user needs a certificate, it will be created.
        """
        session = self.webhelpers.traversed_session.session

        if (
            Session.query(model.Certificate)
            .filter(model.Certificate.session_id == session.session_id)
            .count()
        ):
            return

        # TODO: get rid of this write on read
        alsoProvides(self.request, IDisableCSRFProtection)
        Session.add(
            model.Certificate(
                session_id=session.session_id,
                json=json.dumps({"date": date.today().strftime("%Y-%m-%d")}),
            )
        )

    def can_display_certificate_earned(self):
        """Condition to show the link to the certificate view."""
        country = self.country
        threshold_fullfilled = (
            getattr(country, "certificates_enabled", False)
            and self.completion_percentage >= country.certificate_completion_threshold
        )
        if threshold_fullfilled:
            self.maybe_create_earned_certificate()
        return threshold_fullfilled

    @property
    @memoize
    def certificate(self):
        """Find the certificate associated to this session."""
        return (
            Session.query(model.Certificate)
            .filter(model.Certificate.session_id == self.webhelpers.session_id)
            .one()
        )

    @property
    @memoize
    def certificate_title(self):
        if self.certificate.title:
            return self.certificate.title
        organisation_view = api.content.get_view(
            name="organisation",
            context=self.webhelpers.country_obj,
            request=self.request,
        )
        organisation = self.session.account.organisation
        if organisation:
            return organisation_view.get_organisation_title(organisation)
        return organisation_view.default_organisation_title

    @property
    @memoize
    def certificates(self):
        """Get all certificates associated with this session for display."""
        certificates = super().certificates
        certificate_view = api.content.get_view(
            name="certificate-inner",
            context=self.context,
            request=self.request,
        )
        if certificate_view.can_display_certificate_earned():
            link = f"{self.context.absolute_url()}/@@certificate"
            content = certificate_view()
            certificates.insert(
                0,
                {
                    "link": link,
                    "content": content,
                    "date": certificate_view.certificate.hr_date_plain,
                },
            )
        return certificates

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
        if not self.webhelpers.can_view_session:
            return self.request.response.redirect(self.webhelpers.client_url)
        self.maybe_update()
        return super().__call__()


class OSHACertificateOverview(CertificateOverview):
    """Also show company certificates"""

    @property
    @memoize
    def certificates(self):
        certificates = dict(super().certificates)
        assessments_view = api.content.get_view(
            name="assessments", context=self.context, request=self.request
        )
        for session in assessments_view.sessions:
            traversed_session = session.traversed_session
            certificate_view = api.content.get_view(
                name="certificate-inner",
                context=traversed_session,
                request=self.request,
            )
            if certificate_view.can_display_certificate_earned():
                year = certificate_view.certificate.hr_date_plain.year
                link = f"{traversed_session.absolute_url()}/@@certificate"
                content = certificate_view()
                certificates.setdefault(year, []).append(
                    {
                        "link": link,
                        "content": content,
                        "date": certificate_view.certificate.hr_date_plain,
                    }
                )
        for year, year_certificates in certificates.items():
            certificates[year] = sorted(
                year_certificates, key=lambda c: c["date"], reverse=True
            )
        return certificates.items()


@implementer(IPublishTraverse)
class PublicCertificate(BrowserView):
    """View to publish a public certificate once the hash is known."""

    def publishTraverse(self, request, name):
        self.secret = name
        return self

    @property
    def certificate(self):
        if not getattr(self, "secret", None):
            return None
        query = Session.query(model.Certificate).filter(
            model.Certificate.secret == self.secret
        )
        if query.count():
            return query.one()

    @property
    @memoize
    def certificate_title(self):
        return self.certificate.title

    @property
    @memoize
    def session(self):
        """Find the certificate associated to this session."""
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
        """Try to get a specific adapter for this country that will be used to
        show and handle additional fields in the certificate.

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
        return super().__call__()


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
        self.request.RESPONSE.redirect(f"{self.context.absolute_url()}/@@report")
