# -*- coding: utf-8 -*-
from euphorie.client.model import Session as EuphorieSession
from osha.oira.statistics.model import get_postgres_url
from osha.oira.statistics.utils import UpdateStatisticsDatabases
from osha.oira.statistics.utils import update_tool_info
from Products.Five import BrowserView
from zope import component
from zope import schema

import logging


log = logging.getLogger(__name__)


class UpdateStatistics(BrowserView):
    def get_postgres_url(self):
        return get_postgres_url()

    def __call__(self):
        log.info("Updating statistics databases")
        postgres_url = self.get_postgres_url()
        if postgres_url is None:
            return "Could not get postgres connection URL!"
        update_db = UpdateStatisticsDatabases(EuphorieSession, postgres_url)
        update_db()
        log.info("Done")
        return "Done"


class UpdateToolInfo(BrowserView):
    def __call__(self):
        log.info("Writing survey (tool) information to postgresql")
        surveys = component.getUtility(
            schema.interfaces.IVocabularyFactory, "osha.oira.toolversions"
        )(self.context)

        for survey_path in surveys:
            survey = self.context["sectors"].unrestrictedTraverse(survey_path)
            if not survey.portal_type == "euphorie.survey":
                log.info(
                    "Object is not a survey but inside "
                    "surveygroup, skipping. %s" % "/".join(survey.getPhysicalPath())
                )
                continue

            update_tool_info(survey)

        log.info("Done")
        return "Done"
