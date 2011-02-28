from Acquisition import aq_inner
from zope.component import getMultiAdapter
from five import grok
from euphorie.client import risk
import interfaces

grok.templatedir("templates")

class OSHAMixin():

    def get_language(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
                                (context, self.request), 
                                name=u'plone_portal_state'
                                )
        return portal_state.language()


class OSHAIdentificationView(risk.IdentificationView, OSHAMixin):
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("risk_identification")


class OSHAEvaluationView(risk.EvaluationView, OSHAMixin):
    grok.layer(interfaces.IOSHAEvaluationPhaseSkinLayer)
    grok.template("risk_evaluation")


class OSHAActionPlanView(risk.ActionPlanView, OSHAMixin):
    grok.layer(interfaces.IOSHAActionPlanPhaseSkinLayer)
    grok.template("risk_actionplan")
