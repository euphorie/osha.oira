from euphorie.client.browser.webhelpers import WebHelpers
from logging import getLogger
from osha.oira.client.model import UsersNotInterestedInCertificateStatusBox
from plone.memoize.instance import memoize
from plone.namedfile.interfaces import INamedBlobImage
from z3c.saconfig import Session


log = getLogger(__name__)


class OSHAWebHelpers(WebHelpers):
    show_completion_percentage = True

    @memoize
    def styles_override(self):
        css = super().styles_override
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

    def show_certificate_status_box(self):
        """Check if the current user should see his own certificate status
        box."""
        account_id = self.get_current_account().id
        return (
            Session.query(UsersNotInterestedInCertificateStatusBox)
            .filter(UsersNotInterestedInCertificateStatusBox.account_id == account_id)
            .count()
        ) == 0

    @property
    @memoize
    def custom_js(self):
        survey_path = self.survey_zodb_path()
        if survey_path == "es/covid/covid-19-es":
            return """<script> (function(h,o,t,j,a,r){ h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)}; h._hjSettings={hjid:2105944,hjsv:6}; a=o.getElementsByTagName('head')[0]; r=o.createElement('script');r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv; a.appendChild(r); })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv='); </script> """  # noqa: E501
        elif survey_path == "es/covid/covid-19-es-classic-integration":
            return """<script> (function(h,o,t,j,a,r){ h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)}; h._hjSettings={hjid:2105946,hjsv:6}; a=o.getElementsByTagName('head')[0]; r=o.createElement('script');r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv; a.appendChild(r); })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv='); </script>"""  # noqa: E501

        elif survey_path == "es/covid/covid-19-es-measures-no-integration":
            return """<script> (function(h,o,t,j,a,r){ h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)}; h._hjSettings={hjid:2105949,hjsv:6}; a=o.getElementsByTagName('head')[0]; r=o.createElement('script');r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv; a.appendChild(r); })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv='); </script>"""  # noqa: E501
        elif survey_path == "es/covid/covid-19-es-measures-integration":
            return """<script> (function(h,o,t,j,a,r){ h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)}; h._hjSettings={hjid:2105952,hjsv:6}; a=o.getElementsByTagName('head')[0]; r=o.createElement('script');r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv; a.appendChild(r); })(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv='); </script>"""  # noqa: E501
        else:
            return ""
