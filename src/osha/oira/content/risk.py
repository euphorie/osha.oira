from five import grok
from euphorie.content import risk
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


class Add(risk.Add, OSHAFormMixin):
    """ Override to allow us to dynamically set field descriptions
    """
    grok.context(risk.IRisk)
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


class Edit(risk.Edit, OSHAFormMixin):
    """ Override to allow us to dynamically set field descriptions
    """
    grok.context(risk.IRisk)
    grok.layer(IOSHAContentSkinLayer)

    def __init__(self, context, request):
        risk.Edit.__init__(self, context, request)
        self.evaluation_algorithm = context.evaluation_algorithm()

    def updateFields(self):
        super(Edit, self).updateFields()
        self.setDynamicDescriptions()
        self.buttons['save'].title = _(
            u'button_save_changes', default=u"Save changes")
        self.buttons['cancel'].title = _(u'button_cancel', default=u"Cancel")
