from mobile.sniffer.detect import detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent
from five import grok
from Acquisition import aq_inner
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName
from euphorie.client.sector import IClientSector
from euphorie.client.utils import WebHelpers
from euphorie.content.survey import ISurvey
from .interfaces import IOSHAClientSkinLayer

grok.templatedir('templates')


class OSHAWebHelpers(WebHelpers):
    """ Override Euphorie's webhelpers to add some more utility methods.
    """
    grok.layer(IOSHAClientSkinLayer)
    grok.template('webhelpers')
    grok.name('webhelpers')

    def language_dict(self):
        site = getSite()
        ltool = getToolByName(site, 'portal_languages')
        return ltool.getAvailableLanguages()

    def on_mobile(self):
        """ Return True if the site is being browsed on a mobile phone.
        """
        ua = get_user_agent(self.request)
        if ua:
            if detect_mobile_browser(ua):
                return True
            else:
                return False
        return False

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
        ltool = getToolByName(self.context, 'portal_languages')
        # Only the countries in the client obj should be considered, as the
        # others are not accessible
        for country in client.values():
            ldict = {}
            for sector in country.values():
                if not IClientSector.providedBy(sector):
                    continue
                for survey in sector.objectValues():
                    lang = survey.language
                    if not lang:
                        continue

                    if not ISurvey.providedBy(survey):
                        continue
                    if getattr(survey, "preview", False):
                        continue
                    supported_langs = ltool.getSupportedLanguages()
                    if lang not in supported_langs:
                        base_lang = lang.split('-')[0].strip()
                        if base_lang in supported_langs:
                            ldict[base_lang] = 'dummy'
                        continue
                    ldict[lang] = 'dummy'

            if ldict:
                resp[country.id] = ldict.keys()
        return resp
