from euphorie.client import MessageFactory as _
from osha.oira.ploneintranet.quaive_mixin import QuaiveEditFormMixin
from z3c.form import button
from z3c.form import form


class SurveyQuaiveVersionsForm(QuaiveEditFormMixin, form.Form):
    """Custom edit form designed to be embedded in Quaive"""

    label = _("label_survey_publishing", default="Publishing this survey")

    @button.buttonAndHandler(_("button_publish", default="Publish"))
    def handlePublish(self, action):
        self.request.response.redirect(
            f"{self.context.absolute_url()}/@@quaive-publish"
        )

    @button.buttonAndHandler(_("button_unpublish", default="Unpublish"))
    def handleUnpublish(self, action):
        self.request.response.redirect(
            f"{self.context.absolute_url()}/@@quaive-unpublish"
        )

    @button.buttonAndHandler(_("button_cancel", default="Cancel"))
    def handleCancel(self, action):
        self.request.response.redirect(f"{self.context.absolute_url()}/@@quaive-edit")
