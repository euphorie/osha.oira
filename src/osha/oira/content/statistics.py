# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.CMFPlone.utils import safe_unicode
from Products.statusmessages.interfaces import IStatusMessage
from datetime import datetime
from euphorie.content.country import ICountry
from euphorie.content.sector import ISector
from euphorie.content.sectorcontainer import ISectorContainer
from five import grok
from osha.oira import _
from osha.oira.interfaces import IOSHAContentSkinLayer
from plone import api
from plone.directives import form
from z3c.form import button
from z3c.form.browser.select import SelectFieldWidget
from z3c.form.interfaces import IObjectFactory
from z3c.saconfig import Session
from zope import interface
from zope import schema
from zope.schema._bootstrapinterfaces import RequiredMissing
from zope.component import adapter
from zope.sqlalchemy import datamanager
import logging
import transaction
import urllib2

log = logging.getLogger("osha.oira/browser.statistics")
grok.templatedir('templates')


class IReportPeriod(interface.Interface):
    year = schema.Choice(
        title=_(u'label_year', default=u'Year'),
        vocabulary='osha.oira.report_year',
        required=True,
    )
    period = schema.Choice(
        title=_(u'label_period', default=u'Period'),
        vocabulary='osha.oira.report_period'
    )


class ReportPeriod(object):
    interface.implements(IReportPeriod)

    def __init__(self, value):
        self.year = value['year']
        self.period = value['period']


@adapter(interface.Interface,
         interface.Interface,
         interface.Interface,
         interface.Interface)
class DaysOrMonthsPeriodFactory(object):
    interface.implements(IObjectFactory)

    def __init__(self, context, request, form, widget):
        pass

    def __call__(self, value):
        return ReportPeriod(value)


class StatisticsSchema(form.Schema):
    report_type = schema.Choice(
        title=_(u'label_report_type', default=u'Report Type'),
        vocabulary='osha.oira.report_type',
        required=True,
    )

    countries = schema.Choice(
        title=_(u'label_report_countries', default=u'Country'),
        vocabulary='osha.oira.report_countries',
        required=True,
    )
    form.widget(countries=SelectFieldWidget)

    tools = schema.Choice(
        title=_(u'label_report_tools', default=u'Tool'),
        vocabulary='osha.oira.report_tools',
        required=True,
    )
    form.widget(tools=SelectFieldWidget)

    report_period = schema.Object(
        title=_(u'label_report_period', default=u"Report Period"),
        schema=IReportPeriod,
    )


class WriteStatistics(grok.View):
    grok.context(IPloneSiteRoot)
    grok.require('cmf.ManagePortal')
    grok.name('write-statistics')

    def _walk(self, root, published=False):
        info_surveys = []
        for country in root.objectValues():
            for sector in country.objectValues():
                for survey_or_group in sector.objectValues():
                    surveys = []
                    if survey_or_group.portal_type == 'euphorie.survey':
                        surveys = [survey_or_group]
                        survey_parent_path = '/'.join((country.id, sector.id))
                    elif survey_or_group.portal_type == 'euphorie.surveygroup':
                        surveys = survey_or_group.objectValues()
                        survey_parent_path = '/'.join((country.id,
                                                       sector.id,
                                                       survey_or_group.id))
                    else:
                        log.info('Object is neither survey nor surveygroup, '
                                 'skipping. %s' % '/'.join(
                                     survey_or_group.getPhysicalPath()))
                        continue
                    for survey in surveys:
                        survey_path = '/'.join((survey_parent_path, survey.id))
                        if not survey.portal_type == 'euphorie.survey':
                            log.info('Object is not a survey but inside '
                                     'surveygroup, skipping. %s'
                                     % '/'.join(survey.getPhysicalPath()))
                            continue
                        published_date = None
                        if published:
                            if isinstance(survey.published, datetime):
                                published_date = survey.published
                            elif isinstance(survey.published, tuple):
                                published_date = survey.published[2]
                        info_surveys.append((survey_path,
                                             survey.Language(),
                                             published,
                                             published_date,
                                             survey.created()))

        return info_surveys

    def render(self):
        urltool = getToolByName(self.context, 'portal_url')
        dbtable_surveys = 'statistics_surveys'
        portal = urltool.getPortalObject()
        # published surveys under /client
        info_surveys_client = self._walk(portal['client'], published=True)
        # unpublished surveys under /sectors
        info_surveys_sectors = self._walk(portal['sectors'], published=False)
        info_surveys = info_surveys_client + info_surveys_sectors
        # write to db
        session = Session()
        session.execute('''DELETE FROM %s;''' % dbtable_surveys)

        def clean(value):
            if isinstance(value, basestring):
                return safe_unicode(value).strip().encode('utf-8')
            return value

        def pg_format(value):
            if value is None:
                return 'NULL'
            if isinstance(value, datetime):
                return "TIMESTAMP '%s'" % value.isoformat()
            return "'%s'" % value

        for line in info_surveys:
            insert = '''INSERT INTO %s VALUES %s;''' % \
                     (dbtable_surveys, '(%s)' % ', '.join(map(pg_format,
                      map(clean, line))))
            session.execute(insert)
        datamanager.mark_changed(session)
        transaction.get().commit()

        from pprint import pformat
        return "Written:\n" + pformat(info_surveys)


class StatisticsMixin(object):
    filename = {
        'overview': 'usage_statistics_overview.rptdesign',
        'country': 'usage_statistics_country.rptdesign',
        'tool': 'usage_statistics_tool.rptdesign',
    }

    def _extractData(self):
        """ Wrap z3c.form's extract data to better deal with errors.

            RequiredMissing errors are dependent on the value of report_type.
            So we do some checks here to see whether there really are
            RequiredMissing errors.
        """
        (data, errors) = self.extractData()
        errors = list(errors)
        # z3c.form's object field doesn't properly handle 'required' attr for
        # subelements. We ignore report_period if it's said to be required
        for e in errors:
            if isinstance(e.error, RequiredMissing):
                if e.field.__name__ == 'report_period':
                    data['report_period'] = 0
                    year = self.request.get(
                        'form.widgets.report_period.widgets.year')
                    if year:
                        data['year'] = int(year)
                        errors.remove(e)

        if data.get('report_type') == 'Tool':
            for e in errors:
                if isinstance(e.error, RequiredMissing):
                    if e.field.__name__ == 'countries':
                        errors.remove(e)
        elif data.get('report_type') == 'Country':
            for e in errors:
                if isinstance(e.error, RequiredMissing):
                    if e.field.__name__ == 'tools':
                        errors.remove(e)
        errors = tuple(errors)
        return (data, errors)

    def handle(self):
        (data, errors) = self._extractData()
        if errors:
            IStatusMessage(self.request).add(
                "Please correct the errors", type=u'error')
            return

        sprops = api.portal.get_tool(name='portal_properties').site_properties
        url = sprops.getProperty('birt_report_url')
        if not url:
            IStatusMessage(self.request).add(
                "birt_report_url not set, please contact an administrator",
                type=u'error')
            return

        report_type = data.get('report_type')
        filename = self.filename[report_type]
        url = "&".join([url, '__report=statistics/%s' % filename])
        if report_type == 'country':
            url = "&".join([url, 'country=%s' % self.request.get('country')])
        elif report_type == 'tool':
            url = "&".join([url, 'tool=%s' % self.request.get('tool')])
        elif report_type == 'overview':
            url = "&".join([url, 'sector=%25'])

        year = data.get('year')
        month = 0
        quarter = 0
        period = data.get('report_period')
        if period > 12:
            quarter = period % 12
        else:
            month = period
        url = "&".join([url,
                        'year=%d' % year, 'month=%d' % month, 'quarter=%d' %
                        quarter])
        try:
            page = urllib2.urlopen(url)
        except urllib2.URLError:
            IStatusMessage(self.request).add(
                "Statistics server could not be contacted, please try again "
                "later", type=u'error')
            return
        self.context.REQUEST.response.setHeader(
            'content-type',
            page.headers.get('content-type') or 'application/pdf')
        self.context.REQUEST.response.setHeader(
            'content-disposition',
            page.headers.get('content-disposition') or
            'inline; filename="report.pdf"')
        return page.read()


class CountryStatistics(form.SchemaForm, StatisticsMixin):
    """ Country managers can access statistics for their countries and
        tools inside their respective countries, but nowhere else..
    """
    grok.context(ICountry)
    grok.name('show-statistics')
    grok.require('cmf.ModifyPortalContent')
    grok.layer(IOSHAContentSkinLayer)
    grok.template('statistics')
    schema = StatisticsSchema
    ignoreContext = True
    label = _('title_country_statistics',
              default='Country Statistics Reporting')

    @button.buttonAndHandler(_(u"Submit"))
    def handleSubmit(self, action):
        return self.handle()


class SectorStatistics(form.SchemaForm, StatisticsMixin):
    """ Sector accounts/managers can access statistics for tools in their
        sector, but nowhere else.
    """
    grok.context(ISector)
    grok.name('show-statistics')
    grok.require('cmf.ModifyPortalContent')
    grok.layer(IOSHAContentSkinLayer)
    grok.template('statistics')
    schema = StatisticsSchema
    ignoreContext = True
    label = _('title_sector_statistics',
              default='Sector Statistics Reporting')

    @button.buttonAndHandler(_(u"Submit"))
    def handleSubmit(self, action):
        return self.handle()


class GlobalStatistics(form.SchemaForm, StatisticsMixin):
    """ Site managers can access statistics for the whole site.
    """
    grok.context(ISectorContainer)
    grok.name('show-statistics')
    grok.require('cmf.ModifyPortalContent')
    grok.layer(IOSHAContentSkinLayer)
    grok.template('statistics')
    schema = StatisticsSchema
    ignoreContext = True
    label = _('title_global_statistics',
              default='Global Statistics Reporting')

    @button.buttonAndHandler(_(u"Submit"))
    def handleSubmit(self, action):
        return self.handle()
