from datetime import datetime
from euphorie.content import utils
from euphorie.content.country import ICountry
from euphorie.content.sectorcontainer import ISectorContainer
from euphorie.content.sector import ISector
from five import grok
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from plone import api


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
        items = [('Whole year', 0)]
        items += [(m, i+1) for i, m in enumerate(cal.getMonthNames())]
        items += [('1st Quarter', i+2)]
        items += [('2nd Quarter', i+3)]
        items += [('3rd Quarter', i+4)]
        items += [('4th Quarter', i+5)]
        return SimpleVocabulary.fromItems(items)

grok.global_utility(ReportPeriodVocabulary,
                    name='osha.oira.report_period')


class ReportToolsVocabulary(object):
    """ """
    grok.implements(IVocabularyFactory)

    def getToolsInCountry(self, context):
        tools = []
        for sector in context.values():
            if not ISector.providedBy(sector):
                continue
            for obj in sector.values():
                if obj.portal_type == 'euphorie.survey':
                    tools.append(
                        '/'.join(obj.getPhysicalPath()[-3:]))
                elif obj.portal_type == 'euphorie.surveygroup':
                    tools.extend(
                        ['/'.join(survey.getPhysicalPath()[-4:])
                            for survey in obj.objectValues()])
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
        return SimpleVocabulary.fromValues(tools)

grok.global_utility(ReportToolsVocabulary,
                    name='osha.oira.report_tools')


class ReportCountriesVocabulary(object):
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
        return SimpleVocabulary.fromItems(countries.items())

grok.global_utility(ReportCountriesVocabulary,
                    name='osha.oira.report_countries')

