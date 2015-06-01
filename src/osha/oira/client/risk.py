from Acquisition import aq_inner
from euphorie.client import model
from euphorie.client import risk
from euphorie.client.navigation import FindNextQuestion
from euphorie.client.navigation import FindPreviousQuestion
from euphorie.client.navigation import QuestionURL
from euphorie.client.navigation import getTreeData
from euphorie.client.session import SessionManager
from euphorie.client.update import redirectOnSurveyUpdate
from euphorie.client.utils import HasText
from euphorie.content.solution import ISolution
from five import grok
from z3c.saconfig import Session
from .interfaces import IOSHAIdentificationPhaseSkinLayer
from .interfaces import IOSHAActionPlanPhaseSkinLayer

grok.templatedir("templates")

IMAGE_CLASS = {
    0: '',
    1: 'twelve',
    2: 'six',
    3: 'four',
    4: 'three',
}


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
            self.title = self.context.parent.title
            self.show_info = self.risk.image or \
                HasText(self.risk.description) or \
                HasText(self.risk.legal_reference)
            number_images = getattr(self.risk, 'image', None) and 1 or 0
            if number_images:
                for i in range(2, 5):
                    number_images += getattr(
                        self.risk, 'image{0}'.format(i), None) and 1 or 0
            self.has_images = number_images > 0
            self.number_images = number_images
            self.image_class = IMAGE_CLASS[number_images]
            super(risk.EvaluationView, self).update()


class OSHAActionPlanView(risk.ActionPlanView):
    grok.layer(IOSHAActionPlanPhaseSkinLayer)
    grok.template("risk_actionplan")

    def update(self):
        if redirectOnSurveyUpdate(self.request):
            return

        context = aq_inner(self.context)
        self.errors = {}
        if self.request.environ["REQUEST_METHOD"] == "POST":
            reply = self.request.form
            session = Session()
            errors = False
            reply["action_plans"] = []
            new_plans = []

            for i in range(0, len(reply['measure'])):
                measure = dict([p for p in reply['measure'][i].items()
                                if p[1].strip()])
                reply['action_plans'].append(measure)
                start = measure.get('planning_start')
                end = measure.get('planning_end')
                if start and end and start > end:
                    reply['action_plans'][-1]['errors'][
                        'planning_start_date'] = [
                            u'Start date is not before end date']

                if len(measure):
                    new_plans.append(
                        model.ActionPlan(
                            action_plan=measure.get("action_plan"),
                            prevention_plan=measure.get("prevention_plan"),
                            requirements=measure.get("requirements"),
                            responsible=measure.get("responsible"),
                            budget=measure.get("budget"),
                            planning_start=measure.get('planning_start'),
                            planning_end=measure.get('planning_start')
                        )
                    )
            if errors:
                self.data = reply
            else:
                context.comment = reply.get("comment")
                context.priority = reply.get("priority")

                for plan in context.action_plans:
                    session.delete(plan)
                context.action_plans.extend(new_plans)
                SessionManager.session.touch()

                if reply["next"] == "previous":
                    next = FindPreviousQuestion(
                        context, filter=self.question_filter)
                    if next is None:
                        # We ran out of questions, step back to intro page
                        url = "%s/evaluation" \
                              % self.request.survey.absolute_url()
                        self.request.response.redirect(url)
                        return
                else:
                    next = FindNextQuestion(
                        context, filter=self.question_filter)
                    if next is None:
                        # We ran out of questions, proceed to the report
                        url = "%s/report" % self.request.survey.absolute_url()
                        self.request.response.redirect(url)
                        return

                url = QuestionURL(
                    self.request.survey, next, phase="actionplan")
                self.request.response.redirect(url)
                return
        else:
            if len(context.action_plans) == 0:
                context.action_plans.append(model.ActionPlan())
            self.data = context

        self.risk = self.request.survey.restrictedTraverse(
            context.zodb_path.split("/"))
        self.title = context.parent.title
        self.tree = getTreeData(
            self.request, context,
            filter=self.question_filter, phase="actionplan")
        self.solutions = [solution for solution in self.risk.values()
                          if ISolution.providedBy(solution)]
        number_images = getattr(self.risk, 'image', None) and 1 or 0
        if number_images:
            for i in range(2, 5):
                number_images += getattr(
                    self.risk, 'image{0}'.format(i), None) and 1 or 0
        self.has_images = number_images > 0
        self.image_class = IMAGE_CLASS[number_images]
        super(risk.ActionPlanView, self).update()
