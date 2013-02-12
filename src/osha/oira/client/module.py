from five import grok
from euphorie.client.module import EvaluationView as ModuleEvaluationView
from euphorie.client.module import ActionPlanView as ModuleActionPlanView
from euphorie.client.module import IdentificationView as \
                                        ModuleIdentificationView
from .. import interfaces

grok.templatedir("templates")


class EvaluationView(ModuleEvaluationView):
    grok.layer(interfaces.IOSHAEvaluationPhaseSkinLayer)
    grok.template("module_evaluation")


class IdentificationView(ModuleIdentificationView):
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("module_identification")


class ActionPlanView(ModuleActionPlanView):
    grok.layer(interfaces.IOSHAActionPlanPhaseSkinLayer)
    grok.template("module_actionplan")
