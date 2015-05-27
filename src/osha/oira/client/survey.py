from Acquisition import aq_inner
from euphorie.client import survey, report
from five import grok
from zope.component import getMultiAdapter
from .interfaces import IOSHAClientSkinLayer
from .interfaces import IOSHAIdentificationPhaseSkinLayer
from .interfaces import IOSHAEvaluationPhaseSkinLayer
from .interfaces import IOSHAActionPlanPhaseSkinLayer
from .interfaces import IOSHAReportPhaseSkinLayer

grok.templatedir("templates")


class OSHASurveyPublishTraverser(survey.SurveyPublishTraverser):
    phases = {
            "identification": IOSHAIdentificationPhaseSkinLayer,
            "evaluation": IOSHAEvaluationPhaseSkinLayer,
            "actionplan": IOSHAActionPlanPhaseSkinLayer,
            "report": IOSHAReportPhaseSkinLayer, }


class OSHAStart(survey.Start):
    """ Override the 'start' page to provide our own template.
    """
    grok.require("euphorie.client.ViewSurvey")
    grok.layer(IOSHAClientSkinLayer)
    grok.template("start")
    grok.name("start")


class OSHAIdentification(survey.Identification):
    """ Override the 'identification' page to provide our own template.
    """
    grok.layer(IOSHAIdentificationPhaseSkinLayer)
    grok.template("identification")
    grok.name("index_html")


class OSHAReportView(report.ReportView):
    """ Override the default view, to add a popup overlay
        asking the user if they want to participate in a survey. #2558

        See euphorie/client/survey.py for more info
    """
    grok.template("report")
    grok.layer(IOSHAClientSkinLayer)

    def get_language(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
                                (context, self.request),
                                name=u'plone_portal_state'
                                )
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
    grok.layer(IOSHAActionPlanPhaseSkinLayer)
    grok.template("actionplan")


class Evaluation(survey.Evaluation):
    """
    Override the evaluation template. Reason: we never want to show help_skip_evaluation,
    even if evaluation_optional should be True.
    OSHA tickets: #8963, #6175
    """
    grok.layer(IOSHAEvaluationPhaseSkinLayer)
    grok.template('evaluation')
