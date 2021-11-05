# coding=utf-8
from euphorie.content.browser import survey
from euphorie.content.profilequestion import IProfileQuestion
from plone import api
from plone.memoize.view import memoize
from zope.component import getMultiAdapter

import z3c.form


class SurveyView(survey.SurveyView):
    def modules_and_profile_questions(self):
        return [
            self._morph(child) for child in self.context.values()
            if child.portal_type != "osha.training_question"
        ]

    def _morph(self, child):
        state = getMultiAdapter((child, self.request), name="plone_context_state")
        return {
            "id": child.id,
            "title": child.title,
            "url": state.view_url(),
            "is_profile_question": IProfileQuestion.providedBy(child),
        }

    @property
    @memoize
    def training_questions(self):
        return self.context.listFolderContents(
            {"portal_type": "osha.training_question"}
        )


class EditForm(survey.EditForm):
    def updateWidgets(self):
        result = super(EditForm, self).updateWidgets()
        evaluation_optional = self.widgets.get("evaluation_optional")
        evaluation_optional.mode = z3c.form.interfaces.HIDDEN_MODE
        if self.context.aq_parent.evaluation_algorithm == "french":
            description_probability = self.widgets.get(
                "IOSHASurvey.description_probability"
            )
            description_probability.mode = z3c.form.interfaces.HIDDEN_MODE
        if not api.portal.get_registry_record(
            "euphorie.use_training_module", default=False
        ):
            self.widgets["IOSHASurvey.enable_web_training"].mode = z3c.form.interfaces.HIDDEN_MODE
        return result

    def updateFields(self):
        super(EditForm, self).updateFields()
        self.fields["measures_text_handling"].field.default = "full"
