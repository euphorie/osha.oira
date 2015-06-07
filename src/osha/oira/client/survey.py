from Acquisition import aq_inner
from Acquisition import aq_parent
from euphorie.client import survey, report
from euphorie.client.navigation import getTreeData
from euphorie.client.update import redirectOnSurveyUpdate
from euphorie.client.navigation import FindFirstQuestion
from euphorie.client.navigation import QuestionURL
from five import grok
from zope.component import getMultiAdapter
from osha.oira.client import interfaces

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
