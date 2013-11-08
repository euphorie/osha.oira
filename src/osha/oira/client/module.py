from Acquisition import aq_inner
from euphorie.client import module
from euphorie.client.update import redirectOnSurveyUpdate
from euphorie.client.navigation import FindNextQuestion
from euphorie.client.navigation import QuestionURL
from euphorie.content.profilequestion import IProfileQuestion
from five import grok
from osha.oira.client import interfaces

grok.templatedir("templates")


class IdentificationView(module.IdentificationView):
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)

    def update(self):
        if redirectOnSurveyUpdate(self.request):
            return

        if self.request.environ["REQUEST_METHOD"] == "POST":
            return super(IdentificationView, self).update()

        context = aq_inner(self.context)
        module = self.request.survey.restrictedTraverse(
                                self.context.zodb_path.split("/"))

        if IProfileQuestion.providedBy(module) and context.depth == 2:
            next = FindNextQuestion(context, filter=self.question_filter)
            if next is None:
                # We ran out of questions, proceed to the evaluation
                url = "%s/evaluation" % self.request.survey.absolute_url()
            else:
                url = QuestionURL(self.request.survey, next, phase="identification")
            return self.request.response.redirect(url)
        else:
            return super(IdentificationView, self).update()


class EvaluationView(module.EvaluationView):
    grok.layer(interfaces.IOSHAEvaluationPhaseSkinLayer)
    grok.template("module_evaluation")


class ActionPlanView(module.ActionPlanView):
    grok.layer(interfaces.IOSHAActionPlanPhaseSkinLayer)
    grok.template("module_actionplan")
