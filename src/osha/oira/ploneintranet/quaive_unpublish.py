from euphorie.client import MessageFactory as _
from euphorie.content.interfaces import SurveyUnpublishEvent
from osha.oira.ploneintranet.quaive_mixin import QuaiveEditFormMixin
from plone import api
from z3c.form import button
from z3c.form import form
from zope.event import notify

import logging


logger = logging.getLogger(__name__)


class UnpublishSurveyQuaiveForm(QuaiveEditFormMixin, form.Form):
    """Custom edit form designed to be embedded in Quaive

    This does what euphorie.content.browser.surveygroup.Unpublish does.
    But here it is called on a Survey instead of a SurveyGroup.
    And it uses z3c.form instead of a BrowserView.
    """

    def nextURL(self):
        return f"{self.context.absolute_url()}/@@quaive-edit"

    @button.buttonAndHandler(_("button_unpublish", default="Unpublish"))
    def handleUnpublish(self, action):
        published_survey = self.context
        wt = api.portal.get_tool("portal_workflow")
        if wt.getInfoFor(published_survey, "review_state") != "published":
            logger.warning(
                "Trying to unpublish survey %s which is not marked as published",
                "/".join(published_survey.getPhysicalPath()),
            )
        else:
            wt.doActionFor(published_survey, "retract")
        notify(SurveyUnpublishEvent(published_survey))
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_("button_cancel", default="Cancel"))
    def handleCancel(self, action):
        self.request.response.redirect(self.nextURL())
