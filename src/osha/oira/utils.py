from Acquisition import aq_inner
from zope.component import getMultiAdapter
from euphorie.client.sector import IClientSector
from euphorie.client.utils import WebHelpers
from euphorie.content.survey import ISurvey
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


def get_unactioned_nodes(ls):
    """ Takes a list of modules and risks and removes all risks that have *not* 
        actioned (i.e does not have at least one valid action plan)
        Also remove all modules that have lost all their risks in the process.

        See https://syslab.com/proj/issues/2885
    """
    unactioned = []
    for n in ls:
        if n.type == 'module':
            unactioned.append(n)

        elif n.type == 'risk':
            if not n.action_plans:
                unactioned.append(n)
            else:
                # It's possible that there is an action plan object, but
                # that it's not yet fully populated
                if n.action_plans[0] == None or \
                        n.action_plans[0].action_plan == None:
                    unactioned.append(n)

    unactioned = remove_empty_modules(unactioned)
    return [u for u in unactioned if u != None]


def get_actioned_nodes(ls):
    """ Takes a list of modules and risks and removes all risks that have been
        actioned (i.e has at least one valid action plan).
        Also remove all modules that have lost all their risks in the process

        See https://syslab.com/proj/issues/2885
    """
    actioned = []
    for n in ls:
        if n.type == 'module':
            actioned.append(n)

        if n.type == 'risk' and len(n.action_plans):
                # It's possible that there is an action plan object, but
                # it's not yet fully populated
                plans = [p.action_plan for p in n.action_plans]
                if plans[0] != None:
                    actioned.append(n)

    actioned = remove_empty_modules(actioned)
    return [e for e in actioned if e != None]


class OSHAWebHelpers(WebHelpers):
    """ Override Euphorie's webhelpers to add some more utility methods.
    """

    def get_language(self):
        """ """
        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
                                (context, self.request), 
                                name=u'plone_portal_state'
                                )
        return portal_state.language()

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
        # Only the countries in the client obj should be considered, as the
        # others are not accessible
        for country in client.objectValues():
            langs = {}
            for sector in country.objectValues():
                if not IClientSector.providedBy(sector):
                    continue
                for survey in sector.objectValues():
                    if not ISurvey.providedBy(survey):
                        continue
                    if getattr(survey, "preview", False):
                        continue
                    # XXX: We strip out the country code to keep things simpler.
                    # Otherwise we will have the same language apearing multiple
                    # times on the front page if the surveys are set in different
                    # variants of the same language code.
                    langs[survey.language.split('-')[0].strip()] = 'dummy'
                    
            # surveys might exist without a language set.
            if langs.has_key(''):
                del langs['']
        
            if langs:
                resp[country.id] = langs.keys()

        return resp
