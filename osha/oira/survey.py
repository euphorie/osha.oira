from five import grok
from z3c.saconfig import Session
from euphorie.client import survey, report
from euphorie.client.session import SessionManager
from osha.oira import model
from sqlalchemy import sql
import interfaces

grok.templatedir("templates")

class OSHASurveyPublishTraverser(survey.SurveyPublishTraverser):
    phases = {
            "identification": interfaces.IOSHAIdentificationPhaseSkinLayer,
            "evaluation": interfaces.IOSHAEvaluationPhaseSkinLayer,
            "actionplan": interfaces.IOSHAActionPlanPhaseSkinLayer,
            "report": interfaces.IOSHAReportPhaseSkinLayer, }

class OSHAActionPlanReportView(report.ActionPlanReportView):
    """
    Overrides the original ActionPlanReportView in euphorie.client.survey.py

    Provides the following extra attributes (as per #1517, #1518):
        unanswered_risk_nodes
        not_present_risk_nodes

    Please refer to original for more details.
    """
    grok.template("report_actionplan")
    grok.layer(interfaces.IOSHAReportPhaseSkinLayer)
    grok.name("view")

    def update(self):
        """ """
        super(OSHAActionPlanReportView, self).update()
        self._extra_updates()

    def _extra_updates(self):
        """ Provides the following extra attributes (as per #1517, #1518):
            - unanswered_risk_nodes
            - not_present_risk_nodes

            Place in a separate method so that OSHAActionPlanReportDownload
            can call it.
        """
        if survey.redirectOnSurveyUpdate(self.request):
            return

        session=Session()
        query=session.query(model.SurveyTreeItem)\
                .filter(model.SurveyTreeItem.session==self.session)\
                .filter(sql.or_(model.MODULE_WITH_UNANSWERED_RISKS_FILTER,
                                model.UNANSWERED_RISKS_FILTER))\
                .order_by(model.SurveyTreeItem.path)
        self.unanswered_nodes=query.all()

        query=session.query(model.SurveyTreeItem)\
                .filter(model.SurveyTreeItem.session==self.session)\
                .filter(sql.or_(model.MODULE_WITH_RISKS_NOT_PRESENT_FILTER,
                                model.RISK_NOT_PRESENT_FILTER))\
                .order_by(model.SurveyTreeItem.path)
        self.risk_not_present_nodes=query.all()


class OSHAIdentificationReport(report.IdentificationReport):
    """
    Overrides the original IdentificationReport in euphorie.client.survey.py
    in order to provide a new template.

    Please refer to original for more details.
    """
    grok.layer(interfaces.IOSHAIdentificationPhaseSkinLayer)
    grok.template("report_identification")


class OSHAActionPlanReportDownload(report.ActionPlanReportDownload, OSHAActionPlanReportView):
    """ Generate and download action report.
    """
    grok.require("euphorie.client.ViewSurvey")
    grok.template("report_actionplan")
    grok.name("download")

    def update(self):
        report.ActionPlanReportDownload.update(self)
        OSHAActionPlanReportView._extra_updates(self)
        return self


