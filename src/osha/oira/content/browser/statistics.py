# -*- coding: utf-8 -*-
from datetime import datetime
from osha.oira import _
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from z3c.form.interfaces import IObjectFactory
from z3c.saconfig import Session
from zope import component
from zope import interface
from zope import schema
from zope.interface import implementer
from zope.sqlalchemy import datamanager

import logging
import sys
import transaction


if sys.version_info[0] >= 3:
    basestring = str


log = logging.getLogger("osha.oira/browser.statistics")


class IReportPeriod(interface.Interface):
    year = schema.Choice(
        title=_(u"label_year", default=u"Year"),
        vocabulary="osha.oira.report_year",
        required=True,
    )
    period = schema.Choice(
        title=_(u"label_period", default=u"Period"),
        vocabulary="osha.oira.report_period",
    )


@implementer(IReportPeriod)
class ReportPeriod(object):
    def __init__(self, value):
        self.year = value["year"]
        self.period = value["period"]


@component.adapter(
    interface.Interface, interface.Interface, interface.Interface, interface.Interface
)
@implementer(IObjectFactory)
class ReportPeriodFactory(object):
    def __init__(self, context, request, form, widget):
        pass

    def __call__(self, value):
        return ReportPeriod(value)


class WriteStatistics(BrowserView):
    def getSurveysInfo(self):
        info_surveys = []
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
            published = survey.aq_parent.published == survey.id
            published_date = None
            if published:
                if isinstance(survey.published, datetime):
                    published_date = survey.published
                elif isinstance(survey.published, tuple):
                    published_date = survey.published[2]

            info_surveys.append(
                (
                    survey_path,
                    survey.Language(),
                    published,
                    published_date,
                    survey.created(),
                )
            )
        return info_surveys

    def render(self):
        log.info("Called: write_statistics")
        dbtable_surveys = "statistics_surveys"
        info_surveys = self.getSurveysInfo()
        # write to db
        session = Session()
        session.execute("""DELETE FROM %s;""" % dbtable_surveys)

        def clean(value):
            if isinstance(value, basestring):
                return safe_unicode(value).strip().encode("utf-8")
            return value

        def pg_format(value):
            if value is None:
                return "NULL"
            if isinstance(value, datetime):
                return "TIMESTAMP '%s'" % value.isoformat()
            return "'%s'" % value

        for line in info_surveys:
            insert = """INSERT INTO %s VALUES %s;""" % (
                dbtable_surveys,
                "(%s)" % ", ".join(map(pg_format, map(clean, line))),
            )
            session.execute(insert)
        datamanager.mark_changed(session)
        transaction.get().commit()
        log.info(
            "Exported statistics on {0} surveys to the DB.".format(len(info_surveys))
        )
        from pprint import pformat

        return "Written:\n" + pformat(info_surveys)
