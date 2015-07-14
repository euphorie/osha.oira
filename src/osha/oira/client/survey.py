from Acquisition import aq_inner
from Acquisition import aq_parent
from decimal import Decimal
from euphorie.client import model
from euphorie.client import survey, report
from euphorie.client.navigation import FindFirstQuestion
from euphorie.client.navigation import QuestionURL
from euphorie.client.navigation import getTreeData
from euphorie.client.session import SessionManager
from euphorie.client.update import redirectOnSurveyUpdate
from five import grok
from osha.oira.client import interfaces
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

    query = """SELECT SUBSTRING(path FROM 1 FOR 3) AS module,
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
            GROUP BY module, status;"""

    def getStatus(self):
        # Note: Optional modules with a yes-answer are not distinguishable
        # from non-optional modules, and ignored.
        session_id = SessionManager.id
        query = self.query % dict(sessionid=session_id)
        session = Session()
        result = session.execute(query).fetchall()
        
        total_ok = 0
        total = 0

        modules = {}
        base_url = "%s/identification" % self.request.survey.absolute_url()
        for row in result:
            module = modules.setdefault(row.module, dict())
            if "url" not in module:
                module["url"] = "%s/%s" % (base_url, int(row.module))
            module["path"] = row.module
            if row.status != "ignore":
                module["total"] = module.get("total", 0) + row.count
                if row.status == 'ok':
                    total_ok += row.count
                total += row.count

            module[row.status] = {'count': row.count}

        titles = dict(session.query(model.Module.path, model.Module.title)
                .filter(model.Module.session_id == session_id)
                .filter(model.Module.path.in_(modules.keys())))

        for module in modules.values():
            module["title"] = titles[module["path"]]

        self.percentage_ok = int(total_ok/Decimal(total)*100)
        self.status = modules.values()
        self.status.sort(key=lambda m: m["path"])
