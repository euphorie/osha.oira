from five import grok
from euphorie.client.module import EvaluationView as ModuleEvaluationView
from euphorie.client.module import ActionPlanView as ModuleActionPlanView
from .interfaces import IOSHAEvaluationPhaseSkinLayer
from .interfaces import IOSHAActionPlanPhaseSkinLayer

grok.templatedir("templates")


class EvaluationView(ModuleEvaluationView):
    grok.layer(IOSHAEvaluationPhaseSkinLayer)
    grok.template("module_evaluation")


class ActionPlanView(ModuleActionPlanView):
    grok.layer(IOSHAActionPlanPhaseSkinLayer)
    grok.template("module_actionplan")
