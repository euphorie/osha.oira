# coding=utf-8

from Products.Five.testbrowser import Browser
from osha.oira.tests.base import OiRAFunctionalTestCase


class EuphorieReportTests(OiRAFunctionalTestCase):
    def testUnicodeReportFilename(self):
        from euphorie.content.tests.utils import BASIC_SURVEY
        from euphorie.client.tests.utils import addSurvey
        from euphorie.client.tests.utils import registerUserInClient
        # Test for http://code.simplon.biz/tracker/euphorie/ticket/156
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = Browser()
        survey_url = self.portal.client.nl["ict"]["software-development"].absolute_url()
        browser.open(survey_url)
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value = u"Sessiøn".encode("utf-8")
        browser.getControl(name="next", index=1).click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Force creation of the company data
        browser.open("%s/report/company" % survey_url)
        # Download the report
        browser.handleErrors = False
        browser.open("%s/report/download" % survey_url)
        self.assertEqual(browser.headers.type, "application/rtf")
        self.assertEqual(browser.headers.get("Content-Disposition"),
                'attachment; filename="Action plan Sessi\xc3\xb8n.rtf"')

    def testInvalidDateDoesNotBreakRendering(self):
        import datetime
        from z3c.saconfig import Session
        from euphorie.client import model
        from euphorie.content.tests.utils import BASIC_SURVEY
        from euphorie.client.tests.utils import addSurvey
        from euphorie.client.tests.utils import registerUserInClient
        # Test for http://code.simplon.biz/tracker/tno-euphorie/ticket/150
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = Browser()
        survey_url = self.portal.client.nl["ict"]["software-development"].absolute_url()
        browser.open(survey_url)
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value = u"Sessiøn".encode("utf-8")
        browser.getControl(name="next", index=1).click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Update the risk
        risk = Session.query(model.Risk).first()
        risk.identification = "no"
        risk.action_plans.append(model.ActionPlan(
            action_plan=u"Do something awesome",
            planning_start=datetime.date(1, 2, 3)))
        # Render the report
        browser.handleErrors = False
        browser.open("http://nohost/plone/client/nl/ict/software-development/report/view")
        # No errors = success

    def testCountryDefaultsToCurrentCountry(self):
        from euphorie.content.tests.utils import BASIC_SURVEY
        from euphorie.client.tests.utils import addSurvey
        from euphorie.client.tests.utils import registerUserInClient
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = Browser()
        survey_url = self.portal.client.nl["ict"]["software-development"].absolute_url()
        browser.open(survey_url)
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value = u"Sessiøn".encode("utf-8")
        browser.getControl(name="next", index=1).click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Check the company data
        browser.open("%s/report/company" % survey_url)
        self.assertEqual(browser.getControl(name="form.widgets.country").value, ["nl"])

    def testCompanySettingsRoundTrip(self):
        from euphorie.content.tests.utils import BASIC_SURVEY
        from euphorie.client.tests.utils import addSurvey
        from euphorie.client.tests.utils import registerUserInClient
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = Browser()
        survey_url = self.portal.client.nl["ict"]["software-development"].absolute_url()
        browser.open(survey_url)
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value = u"Sessiøn".encode("utf-8")
        browser.getControl(name="next", index=1).click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Enter some company data
        browser.open("%s/report/company" % survey_url)
        browser.getControl(name="form.widgets.country").value = ["be"]
        browser.getControl(name="form.widgets.employees").value = ["50-249"]
        browser.getControl(name="form.widgets.conductor").value = ["staff"]
        browser.getControl(name="form.widgets.referer").value = ["trade-union"]
        browser.getControl(name="form.widgets.workers_participated").value = ['True']
        browser.getControl(name="form.buttons.next").click()
        # Make sure all fields validated
        self.assertEqual(browser.url, "%s/report/view" % survey_url)
        # Verify entered data
        browser.open("%s/report/company" % survey_url)
        self.assertEqual(browser.getControl(name="form.widgets.country").value, ["be"])
        self.assertEqual(browser.getControl(name="form.widgets.employees").value, ["50-249"])
        self.assertEqual(browser.getControl(name="form.widgets.conductor").value, ["staff"])
        self.assertEqual(browser.getControl(name="form.widgets.referer").value, ["trade-union"])
        self.assertEqual(browser.getControl(name="form.widgets.workers_participated").value, ["True"])


class ActionPlanTimelineTests(OiRAFunctionalTestCase):
    def ActionPlanTimeline(self, *a, **kw):
        from ..report import ActionPlanTimeline
        return ActionPlanTimeline(*a, **kw)

    def createSurveySession(self):
        from z3c.saconfig import Session
        from euphorie.client import model
        self.sqlsession = Session()
        account = model.Account(loginname=u"jane", password=u"secret")
        self.sqlsession.add(account)
        self.session = model.SurveySession(title=u"Session",
                zodb_path="nl/dining/survey", account=account)
        self.sqlsession.add(self.session)
        self.sqlsession.flush()
        return self.session

    def test_get_measures_order_by_priority(self):
        import datetime
        from euphorie.client import model
        session = self.createSurveySession()
        module = model.Module(
            title=u'Root',
            module_id='1',
            zodb_path='1',
            skip_children=False)
        session.addChild(module)
        module.addChild(model.Risk(
            title=u'Risk 1', risk_id='2', zodb_path='1/2', type='risk',
            priority=u'low', identification='no',
            action_plans=[model.ActionPlan(
                action_plan=u"Do something awesome",
                planning_start=datetime.date(2013, 3, 4))]))
        module.addChild(model.Risk(
            title=u'Risk 2', risk_id='3', zodb_path='1/3', type='risk',
            priority=u'high', identification='no',
            action_plans=[model.ActionPlan(
                action_plan=u"Do something awesome",
                planning_start=datetime.date(2013, 5, 2))]))
        module.addChild(model.Risk(
            title=u'Risk 3', risk_id='4', zodb_path='1/4', type='risk',
            priority=u'medium', identification='no',
            action_plans=[model.ActionPlan(
                action_plan=u"Do something awesome",
                planning_start=datetime.date(2013, 4, 1))]))
        view = self.ActionPlanTimeline(None, None)
        view.session = self.session
        self.assertEqual(
            [risk.priority for (module, risk, measure) in view.get_measures()],
            [u'high', u'medium', u'low'])
