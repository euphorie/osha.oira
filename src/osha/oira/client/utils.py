from .interfaces import IOSHAClientSkinLayer
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from euphorie.client import model
from euphorie.client.sector import IClientSector
from euphorie.client.utils import WebHelpers
from euphorie.content.survey import ISurvey
from five import grok
from mobile.sniffer.detect import detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent
from osha.oira.client import model as oiramodel
from sqlalchemy import sql
from z3c.saconfig import Session
from zope.component.hooks import getSite
import htmllib

grok.templatedir('templates')


def html_unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()


def remove_empty_modules(nodes):
    """ Takes a list of modules and risks.

        Removes modules that don't have any risks in them.
        Modules with submodules (with risks) must however be kept.

        How it works:
        -------------
        Use the 'grow' method to create a tree datastructure that
        mirrors the actual layout of modules and risks.

        Then 'prune' it by removing all branches that end in modules.

        Lastly flatten the tree back into a list and use it to filter the
        original list.
    """
    tree = {}
    ids = []

    def grow(tree, nodes):
        for i in range(0, len(nodes)):
            node = nodes[i]
            inserted = False
            for k in tree.keys():
                if node.path.startswith(k[0]):
                    if tree[k]:
                        grow(tree[k], [node])
                    else:
                        tree[k] = {(node.path, node.type, node.id): {}}
                    inserted = True
                    break
            if not inserted:
                tree[(node.path, node.type, node.id)] = {}

    def prune(tree):
        for k in tree.keys():
            if tree[k]:
                prune(tree[k])

            if not tree[k] and k[1] == 'module':
                del tree[k]

    def flatten(tree):
        for k in tree.keys():
            ids.append(k[2])
            flatten(tree[k])

    grow(tree, nodes)
    prune(tree)
    flatten(tree)
    return [n for n in nodes if n.id in ids]


def get_unactioned_nodes(ls):
    """ Takes a list of modules and risks and removes all risks that have been
        actioned (i.e has at least one valid action plan).
        Also remove all modules that have lost all their risks in the process

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
                if n.action_plans[0] is None or \
                        n.action_plans[0].action_plan is None:
                    unactioned.append(n)

    return remove_empty_modules(unactioned)


def get_actioned_nodes(ls):
    """ Takes a list of modules and risks and removes all risks that are *not*
        actioned (i.e does not have at least one valid action plan)
        Also remove all modules that have lost all their risks in the process.

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
                if plans[0] is not None:
                    actioned.append(n)

    return remove_empty_modules(actioned)


def get_unanswered_nodes(session):
    query = Session().query(model.SurveyTreeItem)\
        .filter(
            sql.and_(
                model.SurveyTreeItem.session == session,
                sql.or_(
                    oiramodel.MODULE_WITH_UNANSWERED_RISKS_FILTER,
                    oiramodel.UNANSWERED_RISKS_FILTER),
                sql.not_(model.SKIPPED_PARENTS)))\
        .order_by(model.SurveyTreeItem.path)
    return query.all()


def get_risk_not_present_nodes(session):
    query = Session().query(model.SurveyTreeItem)\
        .filter(
            sql.and_(
                model.SurveyTreeItem.session == session,
                sql.or_(
                    model.SKIPPED_PARENTS,
                    oiramodel.MODULE_WITH_RISKS_NOT_PRESENT_FILTER,
                    oiramodel.RISK_NOT_PRESENT_FILTER,
                    oiramodel.SKIPPED_MODULE,
                )))\
        .order_by(model.SurveyTreeItem.path)
    return query.all()


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


