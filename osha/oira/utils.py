from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from euphorie.client.utils import WebHelpers

class OSHAWebHelpers(WebHelpers):
    """ Override Euphorie's webhelpers to add some more utility methods.
    """

    def get_sectors_dict(self):
        """ Returns a dictionary with keys being countries (and int. orgs) that
            have sectors inside them and the values being the available survey
            langauges.

            See #2556.
        """ 
        context = aq_inner(self.context)
        sectorsfolder = getattr(context, 'sectors')
        if not sectorsfolder:
            return []

        resp = {}
        catalog = getToolByName(context, 'portal_catalog')
        for country in sectorsfolder.objectValues():
            langs = {}
            surveys = catalog(
                        portal_type='euphorie.survey',
                        path='/'.join(country.getPhysicalPath())
                        )

            if not surveys:
                continue

            for survey in surveys:
                langs[survey.language.split('-')[0]] = 'dummy'

            if langs:
                resp[country.id] = langs.keys()

        return resp
