from five import grok
from euphorie.content.risk import Edit as RiskEditForm
from euphorie.content.risk import Add as RiskAddForm
from ..interfaces import IOSHAContentSkinLayer
from .. import _

grok.templatedir("templates")


class OSHAFormMixin:
    """ """
    def setDynamicDescriptions(self):
        """ Set the evaluation_method description depending on the evaluation
            algorithm (Kinney or French)
        """
        evalgroup = self.groups[self.order.index('header_evaluation')]
        evalfield = evalgroup.fields.get('evaluation_method')
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
    grok.layer(IOSHAContentSkinLayer)

    def updateFields(self):
        super(Add, self).updateFields()
        self.setDynamicDescriptions()
        self.buttons['save'].title = _(
            u'button_save_changes', default=u"Save changes")
        self.buttons['cancel'].title = _(u'button_cancel', default=u"Cancel")

    @property
    def label(self):
        return _(u"Add Risk")


class Edit(RiskEditForm, OSHAFormMixin):
    """ Override to allow us to dynamically set field descriptions
    """
    grok.layer(IOSHAContentSkinLayer)

    def updateFields(self):
        super(Edit, self).updateFields()
        self.setDynamicDescriptions()
        self.buttons['save'].title = _(
            u'button_save_changes', default=u"Save changes")
        self.buttons['cancel'].title = _(u'button_cancel', default=u"Cancel")

