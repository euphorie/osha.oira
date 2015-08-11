from Acquisition import aq_inner
from Acquisition import aq_parent
from decimal import Decimal
from euphorie.client import model
from euphorie.client import survey, report
from euphorie.client.profile import extractProfile
from euphorie.client.navigation import FindFirstQuestion
from euphorie.client.navigation import QuestionURL
from euphorie.client.navigation import getTreeData
from euphorie.client.session import SessionManager
from euphorie.client.update import redirectOnSurveyUpdate
from euphorie.content.survey import ISurvey
from five import grok
from osha.oira import log
from osha.oira import _
from osha.oira.client import interfaces
from .country import ConfirmationDeleteSession
from .country import DeleteSession
from .country import RenameSession
from sqlalchemy import sql
from sqlalchemy import orm
from z3c.saconfig import Session
from zope.component import getMultiAdapter
from zope.i18n import translate


grok.templatedir("templates")


class OSHASurveyPublishTraverser(survey.SurveyPublishTraverser):
    survey.SurveyPublishTraverser.phases.update({
        "identification": interfaces.IOSHAIdentificationPhaseSkinLayer,
        "customization": interfaces.IOSHACustomizationPhaseSkinLayer,
        "evaluation": interfaces.IOSHAEvaluationPhaseSkinLayer,
        "actionplan": interfaces.IOSHAActionPlanPhaseSkinLayer,
        "report": interfaces.IOSHAReportPhaseSkinLayer,
    })


class OSHAView(survey.View):
    """ Override the "select existing session or start a new one" view
    """
    grok.require("euphorie.client.ViewSurvey")
    grok.layer(interfaces.IOSHAClientSkinLayer)
    grok.template("survey_sessions")
    grok.name("index_html")


class OSHAStart(survey.Start):
    """ Override the 'start' page to provide our own template.

        In the Jekyll prototype this is called preparation.html
    """
    grok.require("euphorie.client.ViewSurvey")
    grok.layer(interfaces.IOSHAClientSkinLayer)
    grok.template("start")
    grok.name("start")


class ConfirmationDeleteSurveySession(ConfirmationDeleteSession):
    grok.context(ISurvey)


class DeleteSurveySession(DeleteSession):
    grok.context(ISurvey)


class RenameSurveySession(RenameSession):
    grok.context(ISurvey)


class OSHAIdentification(survey.Identification):
    """ Override the 'identification' page to provide our own template.
    """
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("identification")
    grok.name("index_html")

    def update(self):
        if redirectOnSurveyUpdate(self.request):
            return

        self.survey = survey = aq_parent(aq_inner(self.context))
        question = FindFirstQuestion(filter=self.question_filter)
        if question is not None:
            self.next_url = QuestionURL(
                survey, question, phase="identification")
            self.tree = getTreeData(self.request, question)
        else:
            self.next_url = None


class OSHAReportView(report.ReportView):
    """ Override the default view, to add a popup overlay
        asking the user if they want to participate in a survey. #2558

        See euphorie/client/survey.py for more info
    """
    grok.template("report")
    grok.layer(interfaces.IOSHAClientSkinLayer)

    def get_language(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
            (context, self.request),
            name=u'plone_portal_state')
        return portal_state.language()

    def get_survey_url(self):
        context = aq_inner(self.context)
        site_properties = context.portal_properties.site_properties
        sdict = {}
        if hasattr(site_properties, 'survey_urls'):
            survey_urls = site_properties.survey_urls
            for l in survey_urls:
                t = l.split(" ")
                if len(t) != 2:
                    continue
                lang, url = t
                sdict[lang] = url

        lang = self.get_language()
        if lang in sdict:
            return sdict[lang]
        elif 'en' in sdict:
            return sdict['en']
        else:
            return 'http://www.surveymonkey.com/s/OiRATool'


class OSHAActionPlan(survey.ActionPlan):
    """
    Overrides the original ActionPlanReport in euphorie.client.survey.py
    to provide our own template.

    Please refer to original for more details.
    """
    grok.layer(interfaces.IOSHAActionPlanPhaseSkinLayer)
    grok.template("actionplan")

    def update(self):
        if redirectOnSurveyUpdate(self.request):
            return

        self.survey = survey = aq_parent(aq_inner(self.context))
        question = FindFirstQuestion(filter=self.question_filter)
        if question is not None:
            self.next_url = QuestionURL(survey, question, phase="actionplan")
            self.tree = getTreeData(
                self.request, question,
                filter=self.question_filter, phase="actionplan")
        else:
            self.next_url = None


class Evaluation(survey.Evaluation):
    """
    Override the evaluation template. Reason: we never want to show help_skip_evaluation,
    even if evaluation_optional should be True.
    OSHA tickets: #8963, #6175
    """
    grok.layer(interfaces.IOSHAEvaluationPhaseSkinLayer)
    grok.template('evaluation')


class OSHAStatus(survey.Status):
    """ Override the 'status' page to provide our own template.
    """
    grok.layer(interfaces.IOSHAClientSkinLayer)
    grok.template("status")
    grok.name("status")

    def module_query(self, sessionid, optional_modules):
        if optional_modules:
            omc = """WHEN profile_index != -1 AND zodb_path IN %(modules)s
                        THEN SUBSTRING(path FROM 1 FOR 6)
                    WHEN profile_index = -1 AND zodb_path IN %(modules)s
                        THEN SUBSTRING(path FROM 1 FOR 3) || '000-profile'
            """ % dict(modules=optional_modules)
        else:
            omc = ""
        query = """
            SELECT
                CASE %(OPTIONAL_MODULE_CLAUSE)s
                    WHEN profile_index != -1 AND depth < 2
                    THEN SUBSTRING(path FROM 1 FOR 3)
                END AS module
            FROM tree
            WHERE session_id=%(sessionid)d AND type='module'
            GROUP BY module
            ORDER BY module
        """ % dict(OPTIONAL_MODULE_CLAUSE=omc, sessionid=sessionid)
        return query

    def slicePath(self, path):
        while path:
            yield path[:3].lstrip("0")
            path = path[3:]

    def getModules(self):
        """ Return a list of dicts of all the top-level modules and locations
            belonging to this survey.
        """
        session = Session()
        session_id = SessionManager.id
        base_url = "%s/identification" % self.request.survey.absolute_url()
        profile = extractProfile(self.request.survey, SessionManager.session)
        module_query = self.module_query(
            sessionid=session_id,
            optional_modules=len(profile) and "(%s)" % (','.join(
                ["'%s'" % k for k in profile.keys()])) or None
        )
        module_res = session.execute(module_query).fetchall()
        modules_and_profiles = {}
        for row in module_res:
            if row[0] is not None:
                if row[0].find('profile') > 0:
                    path = row[0][:3]
                    modules_and_profiles[path] = 'profile'
                else:
                    modules_and_profiles[row[0]] = ''
        module_paths = [p[0] for p in session.execute(module_query).fetchall() if p[0] is not None]
        module_paths = modules_and_profiles.keys()
        module_paths = sorted(module_paths)
        parent_node = orm.aliased(model.Module)
        titles = dict(session.query(model.Module.path, model.Module.title)
                .filter(model.Module.session_id == session_id)
                .filter(model.Module.path.in_(module_paths)))

        location_titles = dict(session.query(
                    model.Module.path,
                    parent_node.title
                ).filter(
                        model.Module.session_id == session_id).filter(
                        model.Module.path.in_(module_paths)).filter(
                        sql.and_(
                            parent_node.session_id == session_id,
                            parent_node.depth < model.Module.depth,
                            model.Module.path.like(parent_node.path + "%")
                        )
                ))
        modules = {}
        toc = {}

        lang = getattr(self.request, 'LANGUAGE', 'en')
        title_custom_risks = translate(_(
            'title_other_risks', default=u'Added risks (by you)'), target_language=lang)

        for path in module_paths:
            number = ".".join(self.slicePath(path))
            # top-level module, always include it in the toc
            if len(path) == 3:
                title = titles[path]
                if title == 'title_other_risks':
                    title = title_custom_risks
                toc[path] = {
                    'path': path,
                    'title': title,
                    'locations': [],
                    'number': number,
                }
                # If this is a profile (aka container for locations), skip
                # adding to the list of modules
                if modules_and_profiles[path] == 'profile':
                    continue
            # sub-module (location) or location container
            else:
                if path in location_titles:
                    title = u"{0} - {1}".format(location_titles[path], titles[path])
                    toc[path[:3]]['locations'].append({
                        'path': path,
                        'title': titles[path],
                        'number': number,
                    })
                else:
                    log.warning(
                        "Status: found a path for a submodule {0} for which "
                        "there's no location title.".format(path))
                    continue

            modules[path] = {
                'path': path,
                'title': title,
                'url': '%s/%s' % (base_url, '/'.join(self.slicePath(path))),
                'todo': 0,
                'ok': 0,
                'postponed': 0,
                'risk_with_measures': 0,
                'risk_without_measures': 0,
                'number': number,
            }
        self.tocdata = toc
        return modules

    def getRisks(self, module_paths):
        """ Return a list of risk dicts for risks that belong to the modules
            with paths as specified in module_paths.
        """
        session = Session()
        session_id = SessionManager.id
        child_node = orm.aliased(model.Risk)
        risks = session.query(
                    model.Module.path,
                    child_node.id,
                    child_node.path,
                    child_node.title,
                    child_node.identification,
                    child_node.priority,
                    child_node.risk_type,
                    child_node.zodb_path,
                    child_node.is_custom_risk,
                    child_node.postponed
                ).filter(
                    sql.and_(
                        model.Module.session_id == session_id,
                        model.Module.path.in_(module_paths),
                        sql.and_(
                            child_node.session_id == model.Module.session_id,
                            child_node.depth > model.Module.depth,
                            child_node.path.like(model.Module.path + "%")
                        )
                    )
                )

        return [{
                'module_path': risk[0],
                'id': risk[1],
                'path': risk[2],
                'title': risk[3],
                'identification': risk[4],
                'priority': risk[5],
                'risk_type': risk[6],
                'zodb_path': risk[7],
                'is_custom_risk': risk[8],
                'postponed': risk[9],
            } for risk in risks]

    def getStatus(self):
        """ Gather a list of the modules and locations in this survey as well
            as data around their state of completion.
        """
        base_url = "%s/actionplan" % self.request.survey.absolute_url()
        session = Session()
        total_ok = 0
        total_with_measures = 0
        self.high_risks = {}
        modules = self.getModules()
        risks = self.getRisks([m['path'] for m in modules.values()])
        for r in risks:
            if r['identification'] in ['yes', 'n/a']:
                total_ok += 1
                modules[r['module_path']]['ok'] += 1
            elif r['identification'] == 'no':
                measures = session.query(
                        model.ActionPlan.id
                    ).filter(model.ActionPlan.risk_id == r['id'])
                if measures.count():
                    modules[r['module_path']]['risk_with_measures'] += 1
                    total_with_measures += 1
                else:
                    modules[r['module_path']]['risk_without_measures'] += 1
            elif r['postponed']:
                modules[r['module_path']]['postponed'] += 1
            else:
                modules[r['module_path']]['todo'] += 1

            if r['priority'] == "high":
                if r['identification'] != 'no':
                    if r['risk_type'] not in ['top5']:
                        continue
            else:
                continue
            if r['is_custom_risk']:
                risk_title = r['title']
            else:
                risk_obj = self.request.survey.restrictedTraverse(r['zodb_path'].split('/'))
                if not risk_obj:
                    continue
                if r['identification'] == 'no':
                    risk_title = risk_obj.problem_description
                else:
                    risk_title = r['title']
            url = '%s/%s' % (base_url, '/'.join(self.slicePath(r['path'])))
            if self.high_risks.get(r['module_path']):
                self.high_risks[r['module_path']].append({'title': risk_title, 'path': url})
            else:
                self.high_risks[r['module_path']] = [{'title': risk_title, 'path':url}]
        for key, m in modules.items():
            if m['ok'] + m['postponed'] + m['risk_with_measures'] + m['risk_without_measures'] + m['todo'] == 0:
                del modules[key]
                del self.tocdata[key]
        self.percentage_ok = not len(risks) and 100 or int((total_ok + total_with_measures) / Decimal(len(risks))*100)
        self.status = modules.values()
        self.status.sort(key=lambda m: m["path"])
        self.toc = self.tocdata.values()
        self.toc.sort(key=lambda m: m["path"])
