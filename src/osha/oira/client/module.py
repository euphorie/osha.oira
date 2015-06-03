from Acquisition import aq_inner
from Products.statusmessages.interfaces import IStatusMessage
from euphorie.client import model
from euphorie.client import module
from euphorie.client.navigation import FindNextQuestion
from euphorie.client.navigation import QuestionURL
from euphorie.client.navigation import getTreeData
from euphorie.client.session import SessionManager
from euphorie.client.update import redirectOnSurveyUpdate
from euphorie.content import MessageFactory as _
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


class CustomizationView(module.CustomizationView):
    grok.context(model.Module)
    grok.require("euphorie.client.ViewSurvey")
    grok.layer(interfaces.IOSHACustomizationPhaseSkinLayer)
    grok.template("module_customization")

    def update(self):
        if redirectOnSurveyUpdate(self.request):
            return

        context = aq_inner(self.context)
        survey = self.request.survey
        self.module = survey.restrictedTraverse(self.context.zodb_path.split("/"))
        self.title = self.context.title
        self.tree = getTreeData(
                self.request, self.context, phase="identification",
                filter=model.NO_CUSTOM_RISKS_FILTER)

        if self.request.environ["REQUEST_METHOD"] == "POST":
            reply = self.request.form
            if reply.get("next") == "previous":
                url = "%s/identification/%d" % (
                        self.request.survey.absolute_url(),
                        int(self.context.path))
                return self.request.response.redirect(url)

            elif reply.get("next") == "next":
                self.add_custom_risks(reply)
                url = "%s/actionplan" % self.request.survey.absolute_url()
                return self.request.response.redirect(url)

        return super(CustomizationView, self).update()

    def add_custom_risks(self, form):
        session = SessionManager.session
        self.context.removeChildren() # Clear previous custom risks
        for risk_values in form['risk']:
            if not risk_values.get("description") or not risk_values.get("priority"):
                IStatusMessage(self.request).add(
                        _(u"Please fill in the required fields"),
                        type="error")
                self.request.set('errors', {
                    'description': not risk_values.get("description"),
                    'priority': not risk_values.get("priority"),
                });
                return;
            risk = model.Risk(
                comment=risk_values.get('comment'),
                priority=risk_values['priority'],
                risk_id=None,
                risk_type='risk', # XXX Could it also be top5 or policy?
                skip_evaluation=True,
                title=risk_values['description'],
            )
            risk.is_custom_risk = True
            risk.skip_children = False
            risk.postponed = False
            risk.has_description = None
            risk.zodb_path = "/".join([session.zodb_path] + ['customization'] + ['1'])
            risk.profile_index = 0 # XXX: not sure what this is for
            self.context.addChild(risk)
            IStatusMessage(self.request).add(
                    _(u"Your custom risk has been succesfully created."),
                    type="success")


class IdentificationView(module.IdentificationView, Mixin):
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("module_identification")

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
