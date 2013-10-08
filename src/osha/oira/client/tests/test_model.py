from euphorie.client import model
from euphorie.client.tests.database import DatabaseTests
from euphorie.client.tests.test_model import createSurvey
from osha.oira import utils


class ModelQueryTests(DatabaseTests):
    """ Test #7947:

        An optional module, that's marked by the user as not
        applicable, should appear under a query for "risks determined as not
        present". Its contents should NOT appear as unanswered risks.
    """

    def createData(self):
        (self.session, self.survey) = createSurvey()
        self.mod1 = model.Module(
            title=u"Module 1", module_id="1",
            zodb_path="1", skip_children=True)
        self.survey.addChild(self.mod1)
        self.q1 = model.Risk(
            title=u"Risk 1", risk_id="1", zodb_path="1/1",
            type="risk")
        self.mod1.addChild(self.q1)

    def testUnansweredNodes(self):
        self.createData()
        self.assertEqual(len(utils.get_unanswered_nodes(self.survey)), 0)

    def testRiskNotPresentNodes(self):
        self.createData()
        self.assertEqual(len(utils.get_risk_not_present_nodes(self.survey)), 2)


class RiskQueryTests(DatabaseTests):
    """ Test #7547

        A risk with evaluation method 'fixed' (i.e. skip_evaluation=true)
        and which has been identified, should appear in the final report
        as identified but without action plan.
    """

    def createData(self):
        (self.session, self.survey) = createSurvey()
        self.mod1 = model.Module(
            title=u"Module 1",
            module_id="1",
            zodb_path="1",
            skip_children=False
        )
        self.survey.addChild(self.mod1)

        self.q1 = model.Risk(
            title=u"Risk 1",
            risk_id="1",
            zodb_path="1/1",
            type="risk",
            skip_evaluation=1,
            identification="no"
        )
        self.mod1.addChild(self.q1)

    def testUnactionedNodes(self):
        self.createData()
        from z3c.saconfig import Session
        query = Session().query(model.SurveyTreeItem)\
            .filter(model.SurveyTreeItem.session == self.survey)\
            .order_by(model.SurveyTreeItem.path)

        nodes = query.all()
        self.assertEqual(len(utils.get_unactioned_nodes(nodes)), 2)

    def testUnansweredNodes(self):
        self.createData()
        self.assertEqual(len(utils.get_unanswered_nodes(self.survey)), 0)

    def testRiskNotPresentNodes(self):
        self.createData()
        self.assertEqual(len(utils.get_risk_not_present_nodes(self.survey)), 0)
