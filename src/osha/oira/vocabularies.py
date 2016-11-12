from Acquisition import aq_parent
from datetime import datetime
from euphorie.content import utils
from euphorie.content.country import ICountry
from euphorie.content.sector import ISector
from euphorie.content.sectorcontainer import ISectorContainer
from euphorie.content.surveygroup import ISurveyGroup
from five import grok
from osha.oira import _
from plone import api
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.i18n import translate


class ReportTypeVocabulary(object):
    """ """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        t = lambda txt: translate(txt, context=api.portal.get().REQUEST)
        types = {t(_('OiRA Tool')).encode('utf-8'): 'tool'}
        if ISectorContainer.providedBy(context):
            types.update({
                t(_('EU-OSHA Overview')).encode('utf-8'): 'overview',
                t(_('Country')): 'country'
            })
        elif ICountry.providedBy(context):
            types.update({t(_('Country')).encode('utf-8'): 'country'})
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
        t = lambda txt: translate(txt, context=site.REQUEST)
        site = api.portal.get()
        cal = site.REQUEST.locale.dates.calendars['gregorian']
        items = [(t(_(u'Whole year')), 0)]
        items += [(m.encode('utf-8'), i + 1)
                  for i, m in enumerate(cal.getMonthNames())]
        items += [(t(_(u'1st Quarter')).encode('utf-8'), i + 2)]
        items += [(t(_(u'2nd Quarter')).encode('utf-8'), i + 3)]
        items += [(t(_(u'3rd Quarter')).encode('utf-8'), i + 4)]
        items += [(t(_(u'4th Quarter')).encode('utf-8'), i + 5)]
        terms = [
            SimpleVocabulary.createTerm(value, value, token)
            for (token, value) in items]
        return SimpleVocabulary(terms)

grok.global_utility(ReportPeriodVocabulary,
                    name='osha.oira.report_period')


class ToolVersionsVocabulary(object):
    """ """
    grok.implements(IVocabularyFactory)

    def getToolVersionsInSector(self, sector):
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

    def getToolVersionsInCountry(self, country):
        tools = []
        for sector in country.values():
            if not ISector.providedBy(sector):
                continue
            tools += self.getToolVersionsInSector(sector)
        return tools

    def __call__(self, context):
        tools = []
        site = api.portal.get()
        for country in site['sectors'].values():
            if not ICountry.providedBy(country):
                continue
            tools += self.getToolVersionsInCountry(country)
        return tools

grok.global_utility(ToolVersionsVocabulary,
                    name='osha.oira.toolversions')


class PublishedToolsVocabulary(object):
    """ """
    grok.implements(IVocabularyFactory)

    def getToolsInSector(self, sector):
        tools = []
        for obj in sector.values():
            if obj.portal_type == 'euphorie.surveygroup' and \
                    getattr(obj, 'published', None):
                tools += ['/'.join(obj.getPhysicalPath()[-3:])]
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
        elif ISurveyGroup.providedBy(context):
            tools += self.getToolsInSector(aq_parent(context))
        return SimpleVocabulary.fromValues(tools)

grok.global_utility(PublishedToolsVocabulary,
                    name='osha.oira.publishedtools')


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
                                         country.title).encode('utf-8'):
                    country.id
                })
        elif ICountry.providedBy(context):
            countries.update({
                utils.getRegionTitle(
                    context.REQUEST,
                    context.id,
                    context.title).encode('utf-8'): context.id
            })
        elif ISector.providedBy(context) or ISurveyGroup.providedBy(context):
            if ISector.providedBy(context):
                country = aq_parent(context)
            elif ISurveyGroup.providedBy(context):
                country = aq_parent(aq_parent(context))

            if ICountry.providedBy(country):
                countries.update({
                    utils.getRegionTitle(
                        context.REQUEST,
                        country.id,
                        country.title).encode('utf-8'): country.id
                })
        return SimpleVocabulary.fromItems(sorted(countries.items()))

grok.global_utility(CountriesVocabulary,
                    name='osha.oira.countries')


class ReportFileFormatVocabulary(object):
    """ """
    grok.implements(IVocabularyFactory)

    def __call__(self, context):
        formats = [SimpleTerm('xls', token='Excel'),
                   SimpleTerm('pdf', token='PDF'),
                   ]
        return SimpleVocabulary(formats)

grok.global_utility(ReportFileFormatVocabulary,
                    name='osha.oira.report_file_format')
