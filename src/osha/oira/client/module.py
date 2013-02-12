from five import grok
from euphorie.client.module import EvaluationView as ModuleEvaluationView
from euphorie.client.module import ActionPlanView as ModuleActionPlanView
from euphorie.client.module import IdentificationView as \
                                        ModuleIdentificationView
from .interfaces import IOSHAIdentificationPhaseSkinLayer
from .interfaces import IOSHAEvaluationPhaseSkinLayer
from .interfaces import IOSHAActionPlanPhaseSkinLayer

grok.templatedir("templates")


class IdentificationView(ModuleIdentificationView):
    grok.layer(IOSHAIdentificationPhaseSkinLayer)
    grok.template("module_identification")


class EvaluationView(ModuleEvaluationView):
    grok.layer(IOSHAEvaluationPhaseSkinLayer)
    grok.template("module_evaluation")


class ActionPlanView(ModuleActionPlanView):
    grok.layer(IOSHAActionPlanPhaseSkinLayer)
    grok.template("module_actionplan")
