from five import grok
from euphorie.content.risk import Edit as RiskEditForm
from euphorie.content.risk import Add as RiskAddForm
from euphorie.content.solution import ISolution
from plone.directives import form
from plone.directives import dexterity
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


class SolutionEdit(form.SchemaEditForm):
    """ Override to allow us to set form title and button labels """
    grok.context(ISolution)
    grok.require("cmf.ModifyPortalContent")
    grok.layer(IOSHAContentSkinLayer)
    grok.name("edit")

    def updateFields(self):
        super(SolutionEdit, self).updateFields()
        self.buttons['save'].title = _(
            u'button_save_changes', default=u"Save changes")
        self.buttons['cancel'].title = _(u'button_cancel', default=u"Cancel")

    @property
    def label(self):
        return _(u"Edit Solution", default=u"Edit Measure")


class SolutionAdd(dexterity.AddForm):
    """ Override to allow us to set form title and button labels """
    grok.context(ISolution)
    grok.name("euphorie.solution")
    grok.require("euphorie.content.AddNewRIEContent")

    def updateFields(self):
        super(SolutionAdd, self).updateFields()
        self.buttons['save'].title = _(
            u'button_save_changes', default=u"Save changes")
        self.buttons['cancel'].title = _(u'button_cancel', default=u"Cancel")

    @property
    def label(self):
        return _(u"Add Solution", default=u"Add Measure")
