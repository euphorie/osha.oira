# coding=utf-8
from euphorie.client.browser.webhelpers import WebHelpers
from logging import getLogger
from osha.oira.client.model import Certificate
from plone import api
from plone.memoize.instance import memoize
from plone.namedfile.interfaces import INamedBlobImage
from z3c.saconfig import Session

log = getLogger(__name__)


class OSHAWebHelpers(WebHelpers):

    show_completion_percentage = True

    @memoize
    def styles_override(self):

        css = super(OSHAWebHelpers, self).styles_override
        css += """
#osc .miller-columns .browser .item .object-name {
    color: inherit;
}
"""
        return css

    def is_image_small(self, context, fname="image", usecase="module"):
        image = getattr(context, fname, None)
        if image and INamedBlobImage.providedBy(image):
            x, y = image.getImageSize()
            if x < 1000 or y < 430:
                return True

    def maybe_create_earned_certificate(self):
        """ Check if certificates are enabled in this country and if
        the user has earned the certificate for this session.
        In case the user needs a certificate, it will be created.
        """
        certificate_view = api.content.get_view(
            "certificate", self.traversed_session, self.request
        )
        country = certificate_view.country

        if not country.certificates_enabled:
            return

        session = self.traversed_session.session
        if session.completion_percentage < country.certificate_completion_threshold:
            return

        if (
            Session.query(Certificate)
            .filter(Certificate.session_id == session.session_id)
            .first()
        ):
            return
        Session.add(Certificate(session_id=session.session_id))

    def update_completion_percentage(self, session=None):
        completion_percentage = super(
            OSHAWebHelpers, self
        ).update_completion_percentage(session)
        self.maybe_create_earned_certificate()
        return completion_percentage
