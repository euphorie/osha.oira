# -*- coding: utf-8 -*-
from datetime import datetime
from osha.oira import _
from plone import api
from plone.autoform import directives
from plone.supermodel import model
from Products.CMFPlone.utils import safe_unicode
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import form
from z3c.form.browser.select import SelectFieldWidget
from z3c.form.interfaces import IObjectFactory
from z3c.saconfig import Session
from zope import component
from zope import interface
from zope import schema
from zope.interface import implementer
from zope.schema._bootstrapinterfaces import RequiredMissing
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from zope.sqlalchemy import datamanager

import logging
import six
import sys
import transaction


if six.PY2:
    from urllib2 import URLError
    from urllib2 import urlopen
else:
    from urllib.error import URLError
    from urllib.request import urlopen


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


class StatisticsSchema(model.Schema):
    report_type = schema.Choice(
        title=_(u"label_report_type", default=u"Report Type"),
        vocabulary="osha.oira.report_type",
        required=True,
    )

    countries = schema.Choice(
        title=_(u"label_report_countries", default=u"Country"),
        vocabulary="osha.oira.countries",
        required=True,
    )
    directives.widget(countries=SelectFieldWidget)

    tools = schema.Choice(
        title=_(u"label_report_tools", default=u"Tool"),
        vocabulary="osha.oira.publishedtools",
        required=True,
    )
    directives.widget(tools=SelectFieldWidget)

    report_period = schema.Object(
        title=_(u"label_report_period", default=u"Report Period"), schema=IReportPeriod
    )

    file_format = schema.Choice(
        title=_(u"label_report_file_format", default=u"File Format"),
        vocabulary="osha.oira.report_file_format",
        required=True,
    )
    directives.widget(file_format=SelectFieldWidget)

    test_sessions = schema.Choice(
        title=u"How to treat test sessions",
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm(0, title=u"Exclude test sessions from statistics"),
                SimpleTerm(1, title=u"Create statistics exclusively for test sessions"),
            ]
        ),
        required=True,
        default=0,
    )


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


class StatisticsMixin(object):
    filename = {
        "overview": "usage_statistics_overview.rptdesign",
        "country": "usage_statistics_country.rptdesign",
        "tool": "usage_statistics_tool.rptdesign",
        "overview_test": "usage_statistics_overview.rptdesign",
        "country_test": "usage_statistics_country_testsessions.rptdesign",
        "tool_test": "usage_statistics_tool_testsessions.rptdesign",
    }
    pdf_data = None

    def _extractData(self):
        """Wrap z3c.form's extract data to better deal with errors.

        RequiredMissing errors are dependent on the value of report_type.
        So we do some checks here to see whether there really are
        RequiredMissing errors.
        """
        (data, errors) = self.extractData()
        errors = list(errors)
        if data.get("report_type") == "tool":
            for e in errors:
                if isinstance(e.error, RequiredMissing):
                    if e.field.__name__ == "countries":
                        errors.remove(e)
        elif data.get("report_type") == "country":
            for e in errors:
                if isinstance(e.error, RequiredMissing):
                    if e.field.__name__ == "tools":
                        errors.remove(e)
        errors = tuple(errors)
        return (data, errors)

    def getStatisticsServerURL(self, data):
        sprops = api.portal.get_tool(name="portal_properties").site_properties
        url = sprops.getProperty("birt_report_url")
        if not url:
            IStatusMessage(self.request).add(
                "birt_report_url not set, please contact an administrator",
                type=u"error",
            )
            return
        testsessions = data.get("test_sessions", 0)
        report_type = data.get("report_type")
        if testsessions:
            report_type = "{}_test".format(report_type)
        filename = self.filename[report_type]
        url = "&".join([url, "__report=statistics/%s" % filename])
        if report_type.startswith("country"):
            url = "&".join([url, "country=%s" % data.get("countries")])
        elif report_type.startswith("tool"):
            url = "&".join([url, "tool=%s" % data.get("tools")])
        elif report_type.startswith("overview"):
            url = "&".join([url, "sector=%25"])

        report_period = data.get("report_period")
        year = report_period.year
        period = report_period.period
        month = 0
        quarter = 0
        if period > 12:
            quarter = period % 12
        else:
            month = period
        file_format = data.get("file_format")
        url = "&".join(
            [
                url,
                "year=%d" % year,
                "month=%d" % month,
                "quarter=%d" % quarter,
                "testsessions=%d" % testsessions,
                "__format=%s" % file_format,
            ]
        )
        log.info(url)
        return url

    def _handleSubmit(self):
        (data, errors) = self._extractData()
        if errors:
            IStatusMessage(self.request).add(
                "Please fill in all the required fields", type=u"error"
            )
            return

        url = self.getStatisticsServerURL(data)
        if url is None:
            return
        try:
            page = urlopen(url)
        except URLError:
            IStatusMessage(self.request).add(
                "Statistics server could not be contacted, please try again " "later",
                type=u"error",
            )
            return
        self.context.REQUEST.response.setHeader(
            "content-type", page.headers.get("content-type") or "application/pdf"
        )
        self.context.REQUEST.response.setHeader(
            "content-disposition",
            page.headers.get("content-disposition") or 'inline; filename="report.pdf"',
        )
        self.pdf_data = page.read()

    def _is_tool_available(self):
        voc = component.getUtility(IVocabularyFactory, name="osha.oira.publishedtools")(
            self.context
        )
        return bool(voc.by_value)


class CountryStatistics(form.Form, StatisticsMixin):
    """Country managers can access statistics for their countries and
    tools inside their respective countries, but nowhere else..
    """

    schema = StatisticsSchema
    ignoreContext = True
    label = _("title_statistics", default="Statistics Reporting")
    label_detail = _("label_country", default=u"Country")
    template = None
    form_template = ViewPageTemplateFile("templates/statistics.pt")

    @button.buttonAndHandler(
        _(u"Submit"), condition=lambda form: form._is_tool_available()
    )
    def handleSubmit(self, action):
        return self._handleSubmit()

    def render(self):
        if not self._is_tool_available():
            IStatusMessage(self.request).add(
                "No statistics are available as no tools have been " "published yet",
                type=u"warning",
            )

        if self.pdf_data is not None:
            return self.pdf_data
        else:
            self.template = self.form_template
            return self.template()


class SectorStatistics(form.Form, StatisticsMixin):
    """Sector accounts/managers can access statistics for tools in their
    sector, but nowhere else.
    """

    schema = StatisticsSchema
    ignoreContext = True
    label = _("title_statistics", default="Statistics Reporting")
    label_detail = _("Sector", default=u"Sector")
    template = None
    form_template = ViewPageTemplateFile("templates/statistics.pt")

    @button.buttonAndHandler(
        _(u"Submit"), condition=lambda form: form._is_tool_available()
    )
    def handleSubmit(self, action):
        return self._handleSubmit()

    def updateWidgets(self):
        super(SectorStatistics, self).updateWidgets()
        report_type = self.widgets.get("report_type")
        report_type.mode = "hidden"
        report_type.field.default = "tool"

    def render(self):
        if not self._is_tool_available():
            IStatusMessage(self.request).add(
                "No statistics are available as no tools have been " "published yet",
                type=u"warning",
            )

        if self.pdf_data is not None:
            return self.pdf_data
        else:
            self.template = self.form_template
            return self.template()


class GlobalStatistics(form.Form, StatisticsMixin):
    """Site managers can access statistics for the whole site."""

    schema = StatisticsSchema
    ignoreContext = True
    label = _("title_statistics", default="Statistics Reporting")
    label_detail = _("label_global", default=u"Global")
    template = None
    form_template = ViewPageTemplateFile("templates/statistics.pt")

    @button.buttonAndHandler(_(u"Submit"))
    def handleSubmit(self, action):
        return self._handleSubmit()

    def render(self):
        if self.pdf_data is not None:
            return self.pdf_data
        else:
            self.template = self.form_template
            return self.template()
