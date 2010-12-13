from five import grok
from z3c.saconfig import Session
from euphorie.client.survey import ActionPlanReportView
from euphorie.client.survey import PathGhost
from euphorie.client.survey import IReportPhaseSkinLayer
from euphorie.client.update import redirectOnSurveyUpdate
from euphorie.client.session import SessionManager
from osha.oira import model
from sqlalchemy import sql

grok.templatedir("templates")

class OSHAActionPlanReportView(ActionPlanReportView):
    """
    Overrides the original ActionPlanReportView in euphorie.client.survey.py

    Provides the following extra attributes (as per #1517, #1518):
        unanswered_risk_nodes
        not_present_risk_nodes

    Please refer to original for more details.
    """
    grok.context(PathGhost)
    grok.require("euphorie.client.ViewSurvey")
    grok.template("report_actionplan")
    grok.layer(IReportPhaseSkinLayer)
    grok.name("view")

    def update(self):
        if redirectOnSurveyUpdate(self.request):
            return

        session=Session()
        self.session=SessionManager.session
        if self.session.company is None:
            self.session.company=model.Company()
        query=session.query(model.SurveyTreeItem)\
                .filter(model.SurveyTreeItem.session==self.session)\
                .filter(sql.not_(model.SKIPPED_PARENTS))\
                .filter(sql.or_(model.MODULE_WITH_RISK_OR_TOP5_FILTER,
                                model.RISK_PRESENT_OR_TOP5_FILTER))\
                .order_by(model.SurveyTreeItem.path)
        self.nodes=query.all()

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

