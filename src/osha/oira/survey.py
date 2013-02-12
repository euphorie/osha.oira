import z3c.form
from five import grok
from zope.component import getMultiAdapter
from plone.directives import dexterity
from euphorie.content.profilequestion import IProfileQuestion
from euphorie.content.survey import View as SurveyView
from euphorie.content.survey import ISurvey
from .interfaces import IOSHAContentSkinLayer

grok.templatedir("templates")


class OSHASurveyEditForm(dexterity.EditForm):
    grok.context(ISurvey)

    def updateWidgets(self):
        result = super(OSHASurveyEditForm, self).updateWidgets()
        widget = self.widgets.get('evaluation_optional')
        widget.mode = z3c.form.interfaces.HIDDEN_MODE
        return result


class OSHASurveyView(SurveyView):
    grok.layer(IOSHAContentSkinLayer)
    grok.template("survey_view")

    def modules_and_profile_questions(self):
        return [self._morph(child) for child in self.context.values()]

    def _morph(self, child):
        state = getMultiAdapter(
                    (child, self.request),
                    name="plone_context_state")

        return dict(id=child.id,
                    title=child.title,
                    url=state.view_url(),
                    is_profile_question=IProfileQuestion.providedBy(child))
