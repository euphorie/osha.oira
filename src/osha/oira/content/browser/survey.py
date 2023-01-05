from euphorie.content.browser import survey

import z3c.form


class EditForm(survey.EditForm):
    def updateWidgets(self):
        result = super().updateWidgets()
        evaluation_optional = self.widgets.get("evaluation_optional")
        evaluation_optional.mode = z3c.form.interfaces.HIDDEN_MODE
        if self.context.aq_parent.evaluation_algorithm == "french":
            description_probability = self.widgets.get(
                "IOSHASurvey.description_probability"
            )
            description_probability.mode = z3c.form.interfaces.HIDDEN_MODE
        return result

    def updateFields(self):
        super().updateFields()
        self.fields["measures_text_handling"].field.default = "full"
