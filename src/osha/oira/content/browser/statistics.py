from datetime import datetime
from osha.oira import _
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from z3c.saconfig import Session
from zope import component
from zope import schema
from zope.schema.interfaces import IVocabularyFactory
from zope.sqlalchemy import datamanager

import logging
import sys
import transaction


if sys.version_info[0] >= 3:
    basestring = str


log = logging.getLogger("osha.oira/browser.statistics")


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
            insert = """INSERT INTO {} VALUES {};""".format(
                dbtable_surveys,
                "(%s)" % ", ".join(map(pg_format, map(clean, line))),
            )
            session.execute(insert)
        datamanager.mark_changed(session)
        transaction.get().commit()
        log.info(f"Exported statistics on {len(info_surveys)} surveys to the DB.")
        from pprint import pformat

        return "Written:\n" + pformat(info_surveys)


class StatisticsMixin(BrowserView):
    def _is_tool_available(self):
        voc = component.getUtility(IVocabularyFactory, name="osha.oira.publishedtools")(
            self.context
        )
        return bool(voc.by_value)

    @property
    def title_detail(self):
        return self.context.Title()


class CountryStatistics(StatisticsMixin):
    """Country managers can access statistics for their countries and tools
    inside their respective countries, but nowhere else.."""

    label = _("title_statistics", default="Statistics Reporting")
    label_detail = _("label_country", default="Country")

    def __call__(self):
        if not self._is_tool_available():
            IStatusMessage(self.request).add(
                "No statistics are available as no tools have been published yet",
                type="warning",
            )

        return self.index()


class SectorStatistics(StatisticsMixin):
    """Sector accounts/managers can access statistics for tools in their
    sector, but nowhere else."""

    label = _("title_statistics", default="Statistics Reporting")
    label_detail = _("Sector", default="Sector")

    def __call__(self):
        if not self._is_tool_available():
            IStatusMessage(self.request).add(
                "No statistics are available as no tools have been published yet",
                type="warning",
            )

        return self.index()


class GlobalStatistics(StatisticsMixin):
    """Site managers can access statistics for the whole site."""

    label = _("title_statistics", default="Statistics Reporting")
    label_detail = _("label_global", default="Global")
    title_detail = None
