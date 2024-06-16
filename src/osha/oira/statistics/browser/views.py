from euphorie.content.surveygroup import ISurveyGroup
from osha.oira.statistics.utils import update_tool_info
from plone import api
from Products.Five import BrowserView

import logging


log = logging.getLogger(__name__)


class UpdateToolInfo(BrowserView):
    def __call__(self):
        log.info("Writing survey (tool) information to postgresql")
        catalog = api.portal.get_tool("portal_catalog")
        brains = catalog(object_provides=ISurveyGroup.__identifier__)
        for brain in brains:
            surveygroup = brain.getObject()
            update_tool_info(surveygroup)

        log.info("Done")
        return "Done"
