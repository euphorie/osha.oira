# coding=utf-8
from Acquisition import aq_parent
from euphorie.content import utils
from euphorie.content.country import ICountry
from euphorie.content.sector import ISector
from euphorie.content.sectorcontainer import ISectorContainer
from euphorie.content.surveygroup import ISurveyGroup
from plone import api
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary


@implementer(IVocabularyFactory)
class ToolVersionsVocabulary(object):
    """ """

    def getToolVersionsInSector(self, sector):
        tools = []
        for obj in sector.values():
            if obj.portal_type == "euphorie.survey":
                tools.append("/".join(obj.getPhysicalPath()[-3:]))
            elif obj.portal_type == "euphorie.surveygroup":
                tools.extend(
                    [
                        "/".join(survey.getPhysicalPath()[-4:])
                        for survey in obj.objectValues()
                    ]
                )
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
        for country in site["sectors"].values():
            if not ICountry.providedBy(country):
                continue
            tools += self.getToolVersionsInCountry(country)
        return tools


ToolVersionsVocabularyFactory = ToolVersionsVocabulary()


@implementer(IVocabularyFactory)
class PublishedToolsVocabulary(object):
    """ """

    def getToolsInSector(self, sector):
        tools = []
        for obj in sector.values():
            if obj.portal_type == "euphorie.surveygroup" and getattr(
                obj, "published", None
            ):
                tools += ["/".join(obj.getPhysicalPath()[-3:])]
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


PublishedToolsVocabularyFactory = PublishedToolsVocabulary()


@implementer(IVocabularyFactory)
class CountriesVocabulary(object):
    """ """

    def __call__(self, context):
        countries = {}
        if ISectorContainer.providedBy(context):
            for country in context.values():
                if not ICountry.providedBy(country):
                    continue
                countries.update(
                    {
                        utils.getRegionTitle(
                            context.REQUEST, country.id, country.title
                        ).encode("utf-8"): country.id
                    }
                )
        elif ICountry.providedBy(context):
            countries.update(
                {
                    utils.getRegionTitle(
                        context.REQUEST, context.id, context.title
                    ).encode("utf-8"): context.id
                }
            )
        elif ISector.providedBy(context) or ISurveyGroup.providedBy(context):
            if ISector.providedBy(context):
                country = aq_parent(context)
            elif ISurveyGroup.providedBy(context):
                country = aq_parent(aq_parent(context))

            if ICountry.providedBy(country):
                countries.update(
                    {
                        utils.getRegionTitle(
                            context.REQUEST, country.id, country.title
                        ).encode("utf-8"): country.id
                    }
                )
        return SimpleVocabulary.fromItems(sorted(countries.items()))


CountriesVocabularyFactory = CountriesVocabulary()
