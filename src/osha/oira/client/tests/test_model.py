from euphorie.client import model
from euphorie.client.tests.database import DatabaseTests
from euphorie.client.tests.utils import createSurvey
from osha.oira.client import utils


class ModelQueryTests(DatabaseTests):
    """ Test #7947:

        An optional module, that's marked by the user as not
        applicable, should appear under a query for "risks determined as not
        present". Its contents should NOT appear as unanswered risks.
    """

    def createData(self):
        (self.session, self.survey) = createSurvey()
        self.mod1 = model.Module(
            title=u"Module 1",
            module_id="1",
            zodb_path="1",
            skip_children=True)

        self.survey.addChild(self.mod1)

        self.q1 = model.Risk(
            title=u"Risk 1",
            risk_id="1",
            zodb_path="1/1",
            type="risk")
        self.mod1.addChild(self.q1)

    def testUnansweredNodes(self):
        self.createData()
        self.assertEqual(len(utils.get_unanswered_nodes(self.survey)), 0)

    def testRiskNotPresentNodes(self):
        self.createData()
        self.assertEqual(len(utils.get_risk_not_present_nodes(self.survey)), 2)


