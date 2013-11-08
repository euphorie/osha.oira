from Acquisition import aq_inner
from euphorie.client import module
from euphorie.client.update import redirectOnSurveyUpdate
from euphorie.client.navigation import FindNextQuestion
from euphorie.client.navigation import QuestionURL
from euphorie.content.profilequestion import IProfileQuestion
from five import grok
from osha.oira.client import interfaces

grok.templatedir("templates")

class Mixin(object):

    def _update(self, superclass):
        if redirectOnSurveyUpdate(self.request):
            return

        if self.request.environ["REQUEST_METHOD"] == "POST":
            return super(superclass, self).update()

        context = aq_inner(self.context)
        module = self.request.survey.restrictedTraverse(
                                self.context.zodb_path.split("/"))

        if IProfileQuestion.providedBy(module) and context.depth == 2:
            next = FindNextQuestion(context, filter=self.question_filter)
            if next is None:
                if self.phase == 'identification':
                    url = "%s/evaluation" % self.request.survey.absolute_url()
                elif self.phase == 'evaluation':
                    url = "%s/actionplan" % \
                            self.request.survey.absolute_url()
                elif self.phase == 'actionplan':
                    url = "%s/report" % self.request.survey.absolute_url()
            else:
                url = QuestionURL(self.request.survey, next, phase=self.phase)
            return self.request.response.redirect(url)
        else:
            return super(superclass, self).update()


class IdentificationView(module.IdentificationView, Mixin):
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)

    def update(self):
        return self._update(IdentificationView)


class EvaluationView(module.EvaluationView, Mixin):
    grok.layer(interfaces.IOSHAEvaluationPhaseSkinLayer)
    grok.template("module_evaluation")

    def update(self):
        return self._update(EvaluationView)


class ActionPlanView(module.ActionPlanView, Mixin):
    grok.layer(interfaces.IOSHAActionPlanPhaseSkinLayer)
    grok.template("module_actionplan")

    def update(self):
        return self._update(ActionPlanView)
