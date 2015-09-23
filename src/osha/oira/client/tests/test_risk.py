# coding=utf-8

from Products.Five.testbrowser import Browser
from euphorie.client.tests.utils import addSurvey
from euphorie.client.tests.utils import registerUserInClient
from osha.oira.tests.base import OiRAFunctionalTestCase


class EuphorieRiskTests(OiRAFunctionalTestCase):

    def testShowFrenchEvaluation(self):
        from euphorie.content.tests.utils import BASIC_SURVEY
        # Test for http://code.simplon.biz/tracker/tno-euphorie/ticket/150
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = Browser()
        survey = self.portal.client.nl["ict"]["software-development"]
        survey.evaluation_algorithm = u"french"
        survey["1"]["2"].type = "risk"
        browser.open(survey.absolute_url())
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value = u"Sessiøn".encode("utf-8")
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
                "http://nohost/plone/client/nl/ict/software-development/actionplan/1/1")
        self.assertEqual(browser.getControl(name="priority").value, ["high"])
