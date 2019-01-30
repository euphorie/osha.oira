# coding=utf-8
from euphorie.client import survey
from five import grok
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
    survey.SurveyPublishTraverser.countries.update(
        {
            'it': {
                'identification': interfaces.IOSHAItalyIdentificationPhaseSkinLayer,
                'customization': interfaces.IOSHAItalyCustomizationPhaseSkinLayer,
                'evaluation': interfaces.IOSHAItalyEvaluationPhaseSkinLayer,
                'actionplan': interfaces.IOSHAItalyActionPlanPhaseSkinLayer,
                'report': interfaces.IOSHAItalyReportPhaseSkinLayer,
            },
            'fr': {
                'identification': interfaces.IOSHAFranceIdentificationPhaseSkinLayer,
                'customization': interfaces.IOSHAFranceCustomizationPhaseSkinLayer,
                'evaluation': interfaces.IOSHAFranceEvaluationPhaseSkinLayer,
                'actionplan': interfaces.IOSHAFranceActionPlanPhaseSkinLayer,
                'report': interfaces.IOSHAFranceReportPhaseSkinLayer,
            },
        }
    )


class OSHAStatusPrint(survey.Status):
    """ Override the 'status' page to provide our own template.
    """
    grok.template("status_print")
    grok.name("status_print")
