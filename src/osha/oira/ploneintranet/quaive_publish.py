from euphorie.client import MessageFactory as _
from euphorie.client.browser.publish import PublishSurvey
from osha.oira.ploneintranet.quaive_mixin import QuaiveEditFormMixin
from z3c.form import button


class PublishSurveyQuaiveForm(QuaiveEditFormMixin, PublishSurvey):
    """Custom edit form designed to be embedded in Quaive
    """

    def nextURL(self):
        return f"{self.context.absolute_url()}/@@quaive-edit"

    @button.buttonAndHandler(_("button_publish", default="Publish"))
    def handlePublish(self, action):
        # Call our super.  Due to the @button we need to add 'self' in the call.
        # The super calls 'self.publish', adds a status message, and redirects to
        # the standard view.  We want a different redirect.  And note that currently
        # the status message is not shown in Quaive.
        super().handlePublish(self, action)
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_("button_cancel", default="Cancel"))
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())
