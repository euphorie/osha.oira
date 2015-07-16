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
from five import grok
from osha.oira.client import interfaces
from sqlalchemy import sql
from sqlalchemy import orm
from z3c.saconfig import Session
from zope.component import getMultiAdapter

grok.templatedir("templates")


class OSHASurveyPublishTraverser(survey.SurveyPublishTraverser):
    survey.SurveyPublishTraverser.phases.update({
        "identification": interfaces.IOSHAIdentificationPhaseSkinLayer,
        "customization": interfaces.IOSHACustomizationPhaseSkinLayer,
        "evaluation": interfaces.IOSHAEvaluationPhaseSkinLayer,
        "actionplan": interfaces.IOSHAActionPlanPhaseSkinLayer,
        "report": interfaces.IOSHAReportPhaseSkinLayer,
    })


class OSHAStart(survey.Start):
    """ Override the 'start' page to provide our own template.

        In the Jekyll prototype this is called preparation.html
    """
    grok.require("euphorie.client.ViewSurvey")
    grok.layer(interfaces.IOSHAClientSkinLayer)
    grok.template("start")
    grok.name("start")


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

    module_query = """SELECT
                    CASE WHEN profile_index != -1 AND zodb_path IN %(optional_modules)s
                            THEN SUBSTRING(path FROM 1 FOR 6)
                         WHEN profile_index != -1
                            THEN SUBSTRING(path FROM 1 FOR 3)
                    END AS module
            FROM tree
            WHERE session_id=%(sessionid)d AND type='module'
            GROUP BY module"""

    query = """SELECT
                    CASE WHEN type='module' AND profile_index != -1 AND zodb_path IN %(optional_modules)s
                            THEN SUBSTRING(path FROM 1 FOR 6)
                         WHEN type!='module' OR profile_index != -1
                            THEN SUBSTRING(path FROM 1 FOR 3)
                    END AS module,

                    CASE WHEN EXISTS(
                                SELECT * FROM tree AS parent_node
                                WHERE tree.session_id=parent_node.session_id AND
                                        tree.depth>parent_node.depth AND
                                        tree.path LIKE parent_node.path || '%%' AND
                                        parent_node.skip_children)
                                THEN 'ignore'
                        WHEN postponed
                                THEN 'postponed'
                        WHEN type='module' AND skip_children='f'
                                THEN 'ignore'
                        WHEN type='module' AND postponed IS NOT NULL
                                THEN 'ok'
                        WHEN type='risk' AND (SELECT identification
                                                FROM risk
                                                WHERE risk.id=tree.id) IN ('yes', 'n/a')
                                THEN 'ok'
                        WHEN type='risk' AND (SELECT identification FROM risk
                                                WHERE risk.id=tree.id AND (SELECT COUNT(id) FROM action_plan WHERE risk.id=action_plan.risk_id)>0
                                             )='no'
                                THEN 'risk_with_measures'
                        WHEN type='risk' AND (SELECT identification FROM risk
                                                WHERE risk.id=tree.id AND (SELECT COUNT(id) FROM action_plan WHERE risk.id=action_plan.risk_id)=0
                                             )='no'
                                THEN 'risk_without_measures'
                        ELSE 'todo'
                    END AS status,
                    COUNT(*) AS count
            FROM tree
            WHERE session_id=%(sessionid)d
            GROUP BY status, module;"""


    def getStatus(self):
        # Note: Optional modules with a yes-answer are not distinguishable
        # from non-optional modules, and ignored.
        base_url = "%s/identification" % self.request.survey.absolute_url()
        session_id = SessionManager.id
        profile = extractProfile(self.request.survey, SessionManager.session)
        query = self.query % dict(
            sessionid=session_id,
            optional_modules="(%s)" % (','.join(["'%s'" % k for k in profile.keys()]))
        )
        session = Session()
        result = session.execute(query).fetchall()

        module_query = self.module_query % dict(
            sessionid=session_id,
            optional_modules="(%s)" % (','.join(["'%s'" % k for k in profile.keys()]))
        )
        module_paths = [p[0] for p in session.execute(module_query).fetchall() if p[0] is not None]

        titles = dict(session.query(model.Module.path, model.Module.title)
                .filter(model.Module.session_id == session_id)
                .filter(model.Module.path.in_(module_paths)))

        # TODO: replace this with a modification of the query above, so that we
        # can get the risks with and without measures as well.
        child_node = orm.aliased(model.Risk)
        risks = session.query(
                    model.Module.path,
                    child_node.path,
                    child_node.title,
                    child_node.identification,
                    child_node.priority,
                    child_node.postponed
                ).filter(
                    sql.and_(
                        model.Module.session_id == session_id,
                        model.Module.path.in_(module_paths),
                        sql.and_(
                            child_node.session_id == model.SurveyTreeItem.session_id,
                            child_node.depth > model.SurveyTreeItem.depth,
                            child_node.path.like(model.SurveyTreeItem.path + "%")
                        )
                    )
                )

        def slice(path):
            while path:
                yield path[:3].lstrip("0")
                path = path[3:]

        modules = {}
        for path in module_paths:
            modules[path] = {
                'path': path,
                'title': titles[path],
                'url': '%s/%s' % (base_url, '/'.join(slice(path))),
                'todo': 0,
                'ok': 0,
                'postponed': 0,
                'risk_with_measures': 0,
                'risk_without_measures': 0
            }

        total_ok = 0
        total = 0
        self.high_risks = {}
        for r in risks:
            if r[3] in ['yes', 'n/a']:
                total_ok += 1
                modules[r[0]]['ok'] += 1
            elif r[3] == 'no':
                # FIXME: we need to differentiate between risks with measures
                # and thos without
                modules[r[0]]['risk_with_measures'] += 1
            elif r[5]:
                modules[r[0]]['postponed'] += 1
            else:
                modules[r[0]]['todo'] += 1

            if r[4] != "high":
                continue
            total += 1
            url = '%s/%s' % (base_url, '/'.join(slice(r[1])))
            if self.high_risks.get(r[0]):
                self.high_risks[r[0]].append({'title':r[2], 'path': url})
            else:
                self.high_risks[r[0]] = [{'title':r[2], 'path':url}]

        self.percentage_ok = int(total_ok/Decimal(total)*100)
        self.status = modules.values()
        self.status.sort(key=lambda m: m["path"])
