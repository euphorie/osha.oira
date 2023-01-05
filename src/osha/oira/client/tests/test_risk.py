from euphorie.client.tests.utils import addSurvey
from euphorie.client.tests.utils import registerUserInClient
from osha.oira.testing import OiRAFunctionalTestCase

import unittest


class EuphorieRiskTests(OiRAFunctionalTestCase):
    @unittest.skip("Can't find DOM node - markup has changed.")
    def testShowFrenchEvaluation(self):
        from euphorie.content.tests.utils import BASIC_SURVEY

        # Test for http://code.simplon.biz/tracker/tno-euphorie/ticket/150
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = self.get_browser()
        survey = self.portal.client.nl["ict"]["software-development"]
        survey.evaluation_algorithm = "french"
        survey["1"]["2"].type = "risk"
        browser.open(survey.absolute_url())
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value = "Sessiøn".encode()
        browser.getControl(name="next").click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Identify the risk
        browser.getControl("next").click()
        browser.getControl(name="answer").value = ["no"]
        # Verify number of options
        self.assertEqual(len(browser.getControl(name="frequency:int").controls), 4)
        self.assertEqual(len(browser.getControl(name="severity:int").controls), 4)
        # # Enter some digits
        browser.getControl(name="frequency:int").value = ["7"]
        browser.getControl(name="severity:int").value = ["10"]
        browser.getControl("next").click()
        browser.open(
            "http://nohost/plone/client/nl/ict/software-development/actionplan/1/1"
        )
        self.assertEqual(browser.getControl(name="priority").value, ["high"])
