# coding=utf-8
from euphorie.content.browser import risk
from osha.oira import _


class OSHAFormMixin:
    """ """

    def setDynamicDescriptions(self):
        """Set the evaluation_method description depending on the evaluation
        algorithm (Kinney or French)
        """
        evalgroup = self.groups[self.order.index("header_evaluation")]
        evalfield = evalgroup.fields.get("evaluation_method")
        if self.evaluation_algorithm == "kinney":
            evalfield.field.description = _(
                "help_evaluation_method_kinney",
                default="Choose between ESTIMATED (rough estimation) or "
                "CALCULATED (combination of probability, frequency "
                "and severity) method.",
            )

        elif self.evaluation_algorithm == "french":
            evalfield.field.description = _(
                "help_evaluation_method_french",
                default="Choose between ESTIMATED (rough estimation) or "
                "CALCULATED (combination of frequency "
                "and severity) method.",
            )


class AddForm(risk.AddForm, OSHAFormMixin):
    """Override to allow us to dynamically set field descriptions"""

    def updateFields(self):
        super(AddForm, self).updateFields()
        self.setDynamicDescriptions()
        self.buttons["save"].title = _(u"button_save_changes", default=u"Save changes")
        self.buttons["cancel"].title = _(u"button_cancel", default=u"Cancel")

    @property
    def label(self):
        return _(u"Add Risk")


class AddView(risk.AddView):
    form = AddForm


class EditForm(risk.EditForm, OSHAFormMixin):
    """Override to allow us to dynamically set field descriptions"""

    def updateFields(self):
        super(EditForm, self).updateFields()
        self.setDynamicDescriptions()
        self.buttons["save"].title = _(u"button_save_changes", default=u"Save changes")
        self.buttons["cancel"].title = _(u"button_cancel", default=u"Cancel")
