from datetime import datetime
from euphorie.client.model import Session as EuphorieSession
from euphorie.client.model import SurveySession
from osha.oira.client.model import SurveyStatistics as Survey

import logging


log = logging.getLogger(__name__)


def list_countries(session_application):
    countries = {
        result[0].split("/")[0]
        for result in session_application.query(SurveySession.zodb_path).distinct()
    }
    return list(countries)


def handle_tool_workflow(obj, event):
    surveygroup = obj.aq_parent
    update_tool_info(surveygroup)


def update_tool_info(surveygroup):
    survey = None
    if surveygroup.published:
        survey = surveygroup.get(surveygroup.published)

    creation_date = survey.created() if survey else surveygroup.created()
    if not isinstance(creation_date, datetime):
        try:
            creation_date = creation_date.asdatetime()
        except AttributeError:
            log.warning("Cannot handle creation date %r", creation_date)
            creation_date = None

    # cut out the part of the ZODB path that's used in postgresql
    # (country / sector / tool)
    zodb_path = "/".join(surveygroup.getPhysicalPath()[-3:])
    published_date = None
    if surveygroup.published and survey:
        if isinstance(survey.published, datetime):
            published_date = survey.published
        elif isinstance(survey.published, tuple):
            published_date = survey.published[2]

    EuphorieSession.query(Survey).filter(Survey.zodb_path == zodb_path).delete()

    EuphorieSession.add(
        Survey(
            zodb_path=zodb_path,
            language=survey.Language() if survey else surveygroup.Language(),
            published=bool(surveygroup.published),
            published_date=published_date,
            creation_date=creation_date,
        )
    )
