from datetime import datetime
from euphorie.content import utils
from euphorie.content.country import ICountry
from euphorie.content.sector import ISector
from euphorie.content.sectorcontainer import ISectorContainer
from five import grok
from osha.oira import _
from plone import api
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


class ReportTypeVocabulary(object):
    """ """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        types = {'Tool': 'tool'}
        if ISectorContainer.providedBy(context):
            types.update({
                'EU-OSHA Overview': 'overview',
                'Country': 'country'
            })
        elif ICountry.providedBy(context):
            types.update({'Country': 'country'})
        return SimpleVocabulary.fromItems(types.items())

grok.global_utility(ReportTypeVocabulary,
                    name='osha.oira.report_type')


class ReportYearVocabulary(object):
    """ """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        return SimpleVocabulary.fromValues(
            range(datetime.now().year, 2010, -1))

grok.global_utility(ReportYearVocabulary,
                    name='osha.oira.report_year')


class ReportPeriodVocabulary(object):
    """ """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        site = api.portal.get()
        cal = site.REQUEST.locale.dates.calendars['gregorian']
        items = [(_(u'Whole year'), 0)]
        items += [(m.encode('utf-8'), i+1)
                  for i, m in enumerate(cal.getMonthNames())]
        items += [(_(u'1st Quarter').encode('utf-8'), i+2)]
        items += [(_(u'2nd Quarter').encode('utf-8'), i+3)]
        items += [(_(u'3rd Quarter').encode('utf-8'), i+4)]
        items += [(_(u'4th Quarter').encode('utf-8'), i+5)]
        return SimpleVocabulary.fromItems(items)

grok.global_utility(ReportPeriodVocabulary,
                    name='osha.oira.report_period')


class ToolsVocabulary(object):
    """ """
    grok.implements(IVocabularyFactory)

    def getToolsInSector(self, sector):
        tools = []
        for obj in sector.values():
            if obj.portal_type == 'euphorie.survey':
                tools.append(
                    '/'.join(obj.getPhysicalPath()[-3:]))
            elif obj.portal_type == 'euphorie.surveygroup':
                tools.extend(
                    ['/'.join(survey.getPhysicalPath()[-4:])
                        for survey in obj.objectValues()])
        return tools

    def getToolsInCountry(self, country):
        tools = []
        for sector in country.values():
            if not ISector.providedBy(sector):
                continue
            tools += self.getToolsInSector(sector)
        return tools

    def __call__(self, context):
        tools = []
        if ISectorContainer.providedBy(context):
            for country in context.values():
                if not ICountry.providedBy(country):
                    continue
                tools += self.getToolsInCountry(country)
        elif ICountry.providedBy(context):
            tools += self.getToolsInCountry(context)
        elif ISector.providedBy(context):
            tools += self.getToolsInSector(context)
        return SimpleVocabulary.fromValues(tools)

grok.global_utility(ToolsVocabulary,
                    name='osha.oira.tools')


class CountriesVocabulary(object):
    """ """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        countries = {}
        if ISectorContainer.providedBy(context):
            for country in context.values():
                if not ICountry.providedBy(country):
                    continue
                countries.update({
                    utils.getRegionTitle(context.REQUEST,
                                         country.id,
                                         country.title):
                    country.id
                })
        elif ICountry.providedBy(context):
            countries.update({
                utils.getRegionTitle(
                    context.REQUEST,
                    context.id,
                    context.title): context.id
            })
        return SimpleVocabulary.fromItems(sorted(countries.items()))

grok.global_utility(CountriesVocabulary,
                    name='osha.oira.countries')

