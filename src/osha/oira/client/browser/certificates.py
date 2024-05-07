from euphorie.client.browser.certificates import View
from plone import api
from plone.memoize.view import memoize


class OSHAView(View):
    """Also show company certificates"""

    @property
    @memoize
    def my_certificates(self):
        certificates = dict(super().my_certificates)
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
                    {"link": link, "content": content}
                )
        return certificates.items()
