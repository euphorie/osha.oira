from euphorie.client import model
from euphorie.client.tests.test_model import createSurvey
from osha.oira.testing import OiRAIntegrationTestCase


class NoCustomRisksFilterTests(OiRAIntegrationTestCase):
    def query(self):
        return self.session.query(model.SurveyTreeItem).filter(
            model.NO_CUSTOM_RISKS_FILTER
        )

    def testQuerying(self):
        (self.session, self.survey) = createSurvey()
        self.mod1 = model.Module(
            title="Module 1", module_id="1", zodb_path="1", skip_children=False
        )
        self.survey.addChild(self.mod1)
        self.q1 = model.Risk(
            title="Risk 1",
            risk_id="1",
            zodb_path="1/1",
            type="risk",
            identification="no",
        )
        self.mod1.addChild(self.q1)
        self.assertEqual(self.query().count(), 2)

        self.q2 = model.Risk(
            title="Risk 2",
            risk_id="2",
            zodb_path="1/2",
            type="risk",
            identification="no",
            is_custom_risk="true",
        )
        self.mod1.addChild(self.q1)
        self.assertEqual(self.query().count(), 2)

        self.q2 = model.Risk(
            title="Risk 3",
            risk_id="2",
            zodb_path="1/3",
            type="risk",
            identification="no",
            is_custom_risk="false",
        )
        self.mod1.addChild(self.q1)
        self.assertEqual(self.query().count(), 2)
