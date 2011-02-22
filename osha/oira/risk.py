from five import grok
from euphorie.client import risk
import interfaces

grok.templatedir("templates")

class OSHAIdentificationView(risk.IdentificationView):
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("risk_identification")

class OSHAEvaluationView(risk.EvaluationView):
    grok.layer(interfaces.IOSHAEvaluationPhaseSkinLayer)
    grok.template("risk_evaluation")

class OSHAActionPlanView(risk.ActionPlanView):
    grok.layer(interfaces.IOSHAActionPlanPhaseSkinLayer)
    grok.template("risk_actionplan")
