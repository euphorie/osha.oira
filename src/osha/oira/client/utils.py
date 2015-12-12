from .interfaces import IOSHAClientSkinLayer
from Acquisition import aq_chain
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from datetime import datetime
from euphorie.client import model
from euphorie.client.sector import IClientSector
from euphorie.content.utils import StripMarkup
from euphorie.client.utils import WebHelpers
from euphorie.content.survey import ISurvey
from euphorie.decorators import reify
from five import grok
from json import dumps
from mobile.sniffer.detect import detect_mobile_browser
from mobile.sniffer.utilities import get_user_agent
from os import path
from osha.oira import _
from osha.oira.client import model as oiramodel
from plone.i18n.normalizer import idnormalizer
from plone.app.controlpanel.site import ISiteSchema
from sqlalchemy import sql
from z3c.saconfig import Session
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.i18nmessageid import MessageFactory
from zope.i18n import translate
from plone import api
import htmllib


pl_message = MessageFactory('plonelocales')
grok.templatedir('templates')


NAME_TO_PHASE = {
    'start': 'preparation',
    'profile': 'preparation',
    'identification': 'identification',
    'customization': 'identification',
    'actionplan': 'actionplan',
    'report': 'report',
    'status': 'status',
    'help': 'help',
    'new-email': 'useraction',
    'account-settings': 'useraction',
    'account-delete': 'useraction',
    'update': 'preparation',
    'disclaimer': 'help',
    'terms-and-conditions': 'help',
}


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

    def __init__(self, context, request):
        super(OSHAWebHelpers, self).__init__(context, request)
        # If the user is anon, but has arrived on a survey. e.g. by following
        # a direct link, save this survey in the request. This allows e.g. to
        # directly open a guest session on a selected survey, instead of
        # showing all the surveys of a sector
        if self.anonymous:
            for obj in aq_chain(aq_inner(self.context)):
                if ISurvey.providedBy(obj):
                    setattr(self.request, 'survey', obj)
                    break

    def get_webstats_js(self):
        site = getSite()
        return ISiteSchema(site).webstats_js

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

    def get_username(self):
        member = api.user.get_current()
        return member.getProperty('fullname') or member.getUserName()

    @reify
    def base_url(self):
        if self.anonymous:
            base_url = self.country_url
            if base_url is not None:
                return base_url
            return self.client_url
        return self._base_url()

    @reify
    def is_outside_of_survey(self):
        return self._base_url() != self.survey_url()

    @reify
    def get_survey_title(self):
        survey = self._survey
        if not survey:
            return None
        return survey.title

    def get_phase(self):
        head, tail = path.split(self.request.PATH_INFO)
        while tail:
            tail = tail.replace('@', '')
            if tail in NAME_TO_PHASE:
                return NAME_TO_PHASE[tail]
            head, tail = path.split(head)
        return ""

    @property
    def came_from_param(self):
        if self.came_from:
            survey_url = self.survey_url()
            if survey_url:
                param = 'came_from={0}'.format(survey_url)
            else:
                param = 'came_from={0}'.format(self.came_from)
        else:
            param = ''
        return param

    @reify
    def get_sector_logo(self):
        sector = self.sector
        if sector is None:
            return None
        images = getMultiAdapter((sector, self.request), name="images")
        return images.scale("logo", height=100, direction="up") or None

    def messages(self):
        status = IStatusMessage(self.request)
        messages = status.show()
        for m in messages:
            m.id = idnormalizer.normalize(m.message)
        return messages

    def _getLanguages(self):
        lt = getToolByName(self.context, "portal_languages")
        lang = lt.getPreferredLanguage()
        if "-" in lang:
            return [lang, lang.split("-")[0], "en"]
        else:
            return [lang, "en"]

    def _findMOTD(self):
        documents = getUtility(ISiteRoot).documents

        motd = None
        for lang in self._getLanguages():
            docs = documents.get(lang, None)
            if docs is None:
                continue
            motd = docs.get("motd", None)
            if motd is not None:
                return motd

    def splash_message(self):
        motd = self._findMOTD()
        if motd:
            now = datetime.now()
            message = dict(
                title=StripMarkup(motd.description), text=motd.body,
                id='{0}{1}'.format(
                    motd.modification_date.strftime('%Y%m%d%H%M%S'),
                    now.strftime('%Y%m%d'))
            )
        else:
            message = None
        return message

    def closetext(self):
        lang = getattr(self.request, 'LANGUAGE', 'en')
        if "-" in lang:
            elems = lang.split("-")
            lang = "{0}_{1}".format(elems[0], elems[1].upper())
        return translate(
            _(u"button_close", default=u"Close"), target_language=lang)


class I18nJSONView(grok.View):
    """ Override Euphorie's webhelpers to add some more utility methods.
    """
    grok.context(Interface)
    grok.layer(IOSHAClientSkinLayer)
    grok.name('date-picker-i18n.json')

    def render(self):
        lang = getattr(self.request, 'LANGUAGE', 'en')
        if "-" in lang:
            lang = lang.split("-")[0]
        json = dumps({
            "months": [
                translate(
                    pl_message(month),
                    target_language=lang) for month in [
                        "month_jan",
                        "month_feb",
                        "month_mar",
                        "month_apr",
                        "month_may",
                        "month_jun",
                        "month_jul",
                        "month_aug",
                        "month_sep",
                        "month_oct",
                        "month_nov",
                        "month_dec",
                ]
            ],
            "weekdays": [
                translate(
                    pl_message(weekday),
                    target_language=lang) for weekday in [
                        "weekday_sun",
                        "weekday_mon",
                        "weekday_tue",
                        "weekday_wed",
                        "weekday_thu",
                        "weekday_fri",
                        "weekday_sat",
                ]
            ],
            "weekdaysShort": [
                translate(
                    pl_message(weekday_abbr),
                    target_language=lang) for weekday_abbr in [
                        "weekday_sun_abbr",
                        "weekday_mon_abbr",
                        "weekday_tue_abbr",
                        "weekday_wed_abbr",
                        "weekday_thu_abbr",
                        "weekday_fri_abbr",
                        "weekday_sat_abbr",
                ]
            ],
        })

        return json
