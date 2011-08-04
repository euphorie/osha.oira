from Acquisition import aq_inner
from zope.component import getMultiAdapter
from five import grok
from euphorie.client import risk
from euphorie.content.risk import Edit as RiskEditForm
from euphorie.content.risk import Add as RiskAddForm
from osha.oira import interfaces
from osha.oira import _

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


class OSHAFormMixin:
    """ """
    def setDynamicDescriptions(self):
        """ Set the evaluation_method description depending on the evaluation
            algorithm (Kinney or French)
        """
        evalgroup = self.groups[self.order.index('header_evaluation')]
        evalfield = evalgroup.fields.get('evaluation_method', None)
        if not evalfield:
            return

        if self.evaluation_algorithm == 'kinney':
            evalfield.field.description = \
                _("help_evaluation_method_kinney",
                default="Choose between ESTIMATED (rough estimation) or "
                        "CALCULATED (combination of probability, frequency "
                        "and severity) method.")

        elif self.evaluation_algorithm == 'french':
            evalfield.field.description = \
                _("help_evaluation_method_french",
                default="Choose between ESTIMATED (rough estimation) or "
                        "CALCULATED (combination of frequency "
                        "and severity) method.")
                

class Add(RiskAddForm, OSHAFormMixin):
    """ Override to allow us to dynamically set field descriptions
    """
    grok.layer(interfaces.IOSHAContentSkinLayer)

    def updateFields(self):
        super(Add, self).updateFields()
        self.setDynamicDescriptions()


class Edit(RiskEditForm, OSHAFormMixin):
    """ Override to allow us to dynamically set field descriptions
    """
    grok.layer(interfaces.IOSHAContentSkinLayer)

    def updateFields(self):
        super(Edit, self).updateFields()
        self.setDynamicDescriptions()

