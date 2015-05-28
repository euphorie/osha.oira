from five import grok
from euphorie.client import risk
from euphorie.client.update import redirectOnSurveyUpdate
from euphorie.client.utils import HasText
from euphorie.client.navigation import getTreeData
from euphorie.client.navigation import FindPreviousQuestion
from euphorie.client.navigation import FindNextQuestion
from euphorie.client.navigation import QuestionURL
from euphorie.client.session import SessionManager
from .interfaces import IOSHAIdentificationPhaseSkinLayer
from .interfaces import IOSHAActionPlanPhaseSkinLayer

grok.templatedir("templates")


class OSHAIdentificationView(risk.EvaluationView):
    """ This view is a combination of the Euphorie Identification and Evauation
        views.
        The risk is both identified and evaluated in this step.
    """
    grok.layer(IOSHAIdentificationPhaseSkinLayer)
    grok.template("risk_identification")

    def update(self):
        if redirectOnSurveyUpdate(self.request):
            return

        self.risk = self.request.survey.restrictedTraverse(
            self.context.zodb_path.split("/"))

        if self.request.environ["REQUEST_METHOD"] == "POST":
            reply = self.request.form
            answer = reply.get("answer")
            self.context.comment = reply.get("comment")
            self.context.postponed = (answer == "postponed")
            if self.context.postponed:
                self.context.identification = None
            else:
                self.context.identification = answer
                if self.risk.evaluation_method == "direct":
                    self.context.priority = reply.get("priority")
                elif self.risk.evaluation_method == 'calculated':
                    self.calculatePriority(self.risk, reply)

            SessionManager.session.touch()

            if reply["next"] == "previous":
                next = FindPreviousQuestion(
                    self.context,
                    filter=self.question_filter)
                if next is None:
                    # We ran out of questions, step back to intro page
                    url = "%s/identification" % \
                        self.request.survey.absolute_url()
                    self.request.response.redirect(url)
                    return
            else:
                next = FindNextQuestion(
                    self.context,
                    filter=self.question_filter)
                if next is None:
                    # We ran out of questions, proceed to the action plan
                    url = "%s/actionplan" % self.request.survey.absolute_url()
                    self.request.response.redirect(url)
                    return

            url = QuestionURL(self.request.survey, next, phase="identification")
            self.request.response.redirect(url)
        else:
            self.tree = getTreeData(self.request, self.context)
            # self.tree = getTreeData(self.request, self.context,
            #     filter=self.question_filter, phase="evaluation")
            self.title = self.context.parent.title
            self.show_info = self.risk.image or \
                HasText(self.risk.description) or \
                HasText(self.risk.legal_reference)

            super(risk.EvaluationView, self).update()


class OSHAActionPlanView(risk.ActionPlanView):
    grok.layer(IOSHAActionPlanPhaseSkinLayer)
    grok.template("risk_actionplan")
