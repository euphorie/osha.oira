from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.ZCatalog.ZCatalog import ZCatalog
from euphorie.client.utils import WebHelpers
from osha.oira.config import lang_dict # Used in templates...

def remove_empty_modules(ls):
    """ Takes a list of modules and risks.

        Removes modules that don't have any risks in them.
        Modules with submodules (with risks) must however be kept.
    """
    while ls and ls[-1].type == 'module':
        ls = ls[:-1]

    for i in range(1, len(ls)):
        if ls[i].type == 'module':
            if ls[i-1].type == 'module' and \
                    ls[i-1].depth >= ls[i].depth:
                ls[i-1] = None
    return ls


def get_unevaluated_nodes(ls):
    """ Takes a list of modules and risks and removes all risks that have *not* 
        been evaluated and actioned.

        Also remove all modules that have lost all their risks in the pocess
    """
    unevaluated = []
    for n in ls:
        if n.type == 'module':
            unevaluated.append(n)

        if n.type == 'risk':
            if n.probability == 0 or not n.action_plans:
                unevaluated.append(n)
            elif len(n.action_plans):
                # It's possible that there is an action plan object, but
                # it's not yet fully populated
                plans = [p.action_plan for p in n.action_plans]
                if plans[0] == None:
                    unevaluated.append(n)

    unevaluated = remove_empty_modules(unevaluated)
    return [u for u in unevaluated if u != None]


def get_evaluated_nodes(ls):
    """ Takes a list of modules and risks and removes all risks that have been
        evaluated and actioned.

        Also remove all modules that have lost all their risks in the pocess
    """
    evaluated = []
    for n in ls:
        if n.type == 'module':
            evaluated.append(n)

        if n.type == 'risk' and n.probability != 0 and len(n.action_plans):
                # It's possible that there is an action plan object, but
                # it's not yet fully populated
                plans = [p.action_plan for p in n.action_plans]
                if plans[0] != None:
                    evaluated.append(n)

    evaluated = remove_empty_modules(evaluated)
    return [e for e in evaluated if e != None]


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

            for s in surveys:
                survey = s._unrestrictedGetObject()
                langs[survey.language.split('-')[0].strip()] = 'dummy'
                
            # surveys might exist without a language set.
            if langs.has_key(''):
                del langs['']
            
            if langs:
                resp[country.id] = langs.keys()

        return resp
