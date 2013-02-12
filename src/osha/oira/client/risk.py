from five import grok
from euphorie.client import risk
from .interfaces import IOSHAIdentificationPhaseSkinLayer
from .interfaces import IOSHAEvaluationPhaseSkinLayer
from .interfaces import IOSHAActionPlanPhaseSkinLayer

grok.templatedir("templates")


class OSHAIdentificationView(risk.IdentificationView):
    grok.layer(IOSHAIdentificationPhaseSkinLayer)
    grok.template("risk_identification")


class OSHAEvaluationView(risk.EvaluationView):
    grok.layer(IOSHAEvaluationPhaseSkinLayer)
    grok.template("risk_evaluation")


class OSHAActionPlanView(risk.ActionPlanView):
    grok.layer(IOSHAActionPlanPhaseSkinLayer)
    grok.template("risk_actionplan")
