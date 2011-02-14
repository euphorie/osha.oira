from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import ZCatalog
from euphorie.client.utils import WebHelpers
from osha.oira.config import lang_dict # Used in templates...

class OSHAWebHelpers(WebHelpers):
    """ Override Euphorie's webhelpers to add some more utility methods.
    """

    def language_dict(self):
        return lang_dict

    def get_sectors_dict(self):
        """ Returns a dictionary with keys being countries (and int. orgs) that
            have sectors inside them and the values being the available survey
            langauges.

            We use ZCatalog directly to bypass permission checks, otherwise we
            get zero surveys returned for anon users.

            See #2556.
        """ 
        context = aq_inner(self.context)
        sectorsfolder = getattr(context, 'sectors')
        if not sectorsfolder:
            return []

        client = getattr(context, 'client')
        if not client:
            return []

        resp = {}
        catalog = getToolByName(context, 'portal_catalog')
        # Only the countries in the client obj should be considered, as the
        # others are not accessible
        for country_id in client.objectIds():
            country = sectorsfolder._getOb(country_id)
            langs = {}
            surveys = ZCatalog.searchResults(
                        catalog,
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
