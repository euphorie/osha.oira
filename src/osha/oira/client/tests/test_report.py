from euphorie.client import model
from euphorie.client.tests.test_model import createSurvey
from osha.oira.client.tests import utils
from osha.oira.testing import OiRAFunctionalTestCase
from osha.oira.testing import OiRAIntegrationTestCase
from z3c.saconfig import Session

import datetime
import unittest


class EuphorieReportTests(OiRAFunctionalTestCase):
    @unittest.skip("Can't find DOM node - markup has changed.")
    def testUnicodeReportFilename(self):
        from euphorie.client.tests.utils import addSurvey
        from euphorie.client.tests.utils import registerUserInClient
        from euphorie.content.tests.utils import BASIC_SURVEY

        # Test for http://code.simplon.biz/tracker/euphorie/ticket/156
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = self.get_browser()
        survey_url = self.portal.client.nl["ict"]["software-development"].absolute_url()
        browser.open(survey_url)
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value = "Sessiøn".encode()
        browser.getControl(name="next").click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Force creation of the company data
        browser.open("%s/report/company" % survey_url)
        # Download the report
        browser.handleErrors = False
        browser.open("%s/report/download" % survey_url)
        self.assertEqual(browser.headers.type, "application/rtf")
        self.assertEqual(
            browser.headers.get("Content-Disposition"),
            'attachment; filename="Action plan Sessi\xc3\xb8n.rtf"',
        )

    @unittest.skip("Can't find DOM node - markup has changed.")
    def testInvalidDateDoesNotBreakRendering(self):
        from euphorie.client.tests.utils import addSurvey
        from euphorie.client.tests.utils import registerUserInClient
        from euphorie.content.tests.utils import BASIC_SURVEY

        # Test for http://code.simplon.biz/tracker/tno-euphorie/ticket/150
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = self.get_browser()
        survey_url = self.portal.client.nl["ict"]["software-development"].absolute_url()
        browser.open(survey_url)
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value = "Sessiøn".encode()
        browser.getControl(name="next").click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Update the risk
        risk = Session.query(model.Risk).first()
        risk.identification = "no"
        risk.action_plans.append(
            model.ActionPlan(
                action_plan="Do something awesome",
                planning_start=datetime.date(1, 2, 3),
            )
        )
        # Render the report
        browser.handleErrors = False
        browser.open(
            "http://nohost/plone/client/nl/ict/" "software-development/report/view"
        )
        # No errors = success

    @unittest.skip("Can't find DOM node - markup has changed.")
    def testCountryDefaultsToCurrentCountry(self):
        from euphorie.client.tests.utils import addSurvey
        from euphorie.client.tests.utils import registerUserInClient
        from euphorie.content.tests.utils import BASIC_SURVEY

        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = self.get_browser()
        survey_url = self.portal.client.nl["ict"]["software-development"].absolute_url()
        browser.open(survey_url)
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value = "Sessiøn".encode()
        browser.getControl(name="next").click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Check the company data
        browser.open("%s/report/company" % survey_url)
        self.assertEqual(browser.getControl(name="form.widgets.country").value, ["nl"])

    @unittest.skip("Can't find DOM node - markup has changed.")
    def testCompanySettingsRoundTrip(self):
        from euphorie.client.tests.utils import addSurvey
        from euphorie.client.tests.utils import registerUserInClient
        from euphorie.content.tests.utils import BASIC_SURVEY

        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser = self.get_browser()
        survey_url = self.portal.client.nl["ict"]["software-development"].absolute_url()
        browser.open(survey_url)
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value = "Sessiøn".encode()
        browser.getControl(name="next").click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Enter some company data
        browser.open("%s/report/company" % survey_url)
        browser.getControl(name="form.widgets.country").value = ["be"]
        browser.getControl(name="form.widgets.employees").value = ["50-249"]
        browser.getControl(name="form.widgets.conductor").value = ["staff"]
        browser.getControl(name="form.widgets.referer").value = ["trade-union"]
        browser.getControl(name="form.widgets.workers_participated").value = ["True"]
        browser.getControl(name="form.buttons.next").click()
        # Make sure all fields validated
        self.assertEqual(browser.url, "%s/report/view" % survey_url)
        # Verify entered data
        browser.open("%s/report/company" % survey_url)
        self.assertEqual(browser.getControl(name="form.widgets.country").value, ["be"])
        self.assertEqual(
            browser.getControl(name="form.widgets.employees").value, ["50-249"]
        )
        self.assertEqual(
            browser.getControl(name="form.widgets.conductor").value, ["staff"]
        )
        self.assertEqual(
            browser.getControl(name="form.widgets.referer").value, ["trade-union"]
        )
        self.assertEqual(
            browser.getControl(name="form.widgets.workers_participated").value, ["True"]
        )


class ActionPlanTimelineTests(OiRAFunctionalTestCase):
    def create_action_plan_timeline(self):
        from osha.oira.client.browser.report import ActionPlanTimeline

        # Add a dynamic type as context to be able to set a "session" attribute on it.
        return ActionPlanTimeline(
            type("context", (object,), {}),
            None,
        )

    def createSurveySession(self):
        self.sqlsession = Session()
        account = model.Account(loginname="jane", password="secret")
        self.sqlsession.add(account)
        self.session = model.SurveySession(
            title="Session", zodb_path="nl/dining/survey", account=account
        )
        self.sqlsession.add(self.session)
        self.sqlsession.flush()
        return self.session

    def test_get_measures_with_nested_modules(self):
        session = self.createSurveySession()
        module = model.Module(
            depth=1,
            title="Root Module",
            module_id="1",
            zodb_path="1",
            skip_children=False,
            profile_index=0,
        )
        session.addChild(module)

        nested_module1 = model.Module(
            depth=2,
            title="Nested Module 1",
            module_id="2",
            zodb_path="1/1",
            skip_children=False,
            profile_index=1,
        )
        module.addChild(nested_module1)

        nested_module2 = model.Module(
            depth=3,
            title="Nested Module 2",
            module_id="3",
            zodb_path="1/1/1",
            skip_children=False,
            profile_index=2,
        )
        nested_module1.addChild(nested_module2)

        risk = model.Risk(
            depth=4,
            title="Floors are washed",
            risk_id="1",
            zodb_path="1/1/1/1",
            type="risk",
            priority="low",
            identification="no",
            action_plans=[
                model.ActionPlan(
                    action_plan="Do something awesome",
                    planning_start=datetime.date(2013, 3, 4),
                )
            ],
        )
        nested_module2.addChild(risk)

        view = self.create_action_plan_timeline()
        view.context.session = self.session
        measures = view.get_measures()
        self.assertEqual(len(measures), 1)
        self.assertEqual(
            measures[0][0].title,
            "Nested Module 2",
        )

    def test_get_measures_with_profile_questions(self):
        """Test for #7322 and #8850."""
        session = self.createSurveySession()
        question = model.Module(
            depth=1,
            title="(Repeatable Module) Do you have multiple shops?",
            module_id="1",
            zodb_path="1",
            skip_children=False,
            profile_index=-1,
        )
        session.addChild(question)

        i = 0
        for module_title in [
            "(Repeating instance) Somerset West",
            "(Repeating instance) Stellenbosch",
        ]:

            answer = model.Module(
                depth=2,
                title=module_title,
                module_id="2",
                zodb_path="1",
                skip_children=False,
                profile_index=i,
            )
            question.addChild(answer)

            answer.addChild(
                model.Risk(
                    depth=3,
                    title="Hands are washed",
                    risk_id="1",
                    zodb_path="1/2",
                    type="risk",
                    priority="low",
                    identification="no",
                    action_plans=[
                        model.ActionPlan(
                            action_plan="Do something awesome",
                            planning_start=datetime.date(2013, 3, 4),
                        )
                    ],
                )
            )
            i += 1

        view = self.create_action_plan_timeline()
        view.context.session = self.session

        measures = view.get_measures()
        self.assertEqual(len(measures), 2)
        self.assertEqual(
            measures[0][0].title,
            "(Repeating instance) Somerset West",
        )
        self.assertEqual(
            measures[1][0].title,
            "(Repeating instance) Stellenbosch",
        )

    def test_get_measures_with_profile_questions_and_submodules(self):
        session = self.createSurveySession()
        question = model.Module(
            depth=1,
            title="(Repeatable Module) Do you have multiple shops?",
            module_id="1",
            zodb_path="1",
            skip_children=False,
            profile_index=-1,
        )
        session.addChild(question)

        i = 0
        for module_title in [
            "(Repeating instance) Somerset West",
            "(Repeating instance) Stellenbosch",
        ]:

            location_path = "%s/%d" % (question.zodb_path, i)
            location = model.Module(
                depth=3,
                title=module_title,
                module_id="2",
                zodb_path=location_path,
                skip_children=False,
                profile_index=i,
            )
            question.addChild(location)

            submodule_path = "%s/1" % location_path
            submodule = model.Module(
                depth=2,
                title="Nested Module 1",
                module_id="2",
                zodb_path="%s/1" % location_path,
                skip_children=False,
                profile_index=1,
            )
            location.addChild(submodule)

            submodule.addChild(
                model.Risk(
                    depth=4,
                    title="Hands are washed",
                    risk_id="1",
                    zodb_path="%s/%d" % (submodule_path, i),
                    type="risk",
                    priority="low",
                    identification="no",
                    action_plans=[
                        model.ActionPlan(
                            action_plan="Do something awesome",
                            planning_start=datetime.date(2013, 3, 4),
                        )
                    ],
                )
            )
            i += 1

        view = self.create_action_plan_timeline()
        view.context.session = self.session
        measures = view.get_measures()
        self.assertEqual(len(measures), 2)
        self.assertEqual(
            measures[0][0].title,
            "Nested Module 1",
        )
        self.assertEqual(
            measures[1][0].title,
            "Nested Module 1",
        )

    def test_get_measures_order_by_priority(self):
        session = self.createSurveySession()
        module = model.Module(
            title="Root", module_id="1", zodb_path="1", skip_children=False
        )
        session.addChild(module)
        module.addChild(
            model.Risk(
                title="Risk 1",
                risk_id="2",
                zodb_path="1/2",
                type="risk",
                priority="low",
                identification="no",
                action_plans=[
                    model.ActionPlan(
                        action_plan="Do something awesome",
                        planning_start=datetime.date(2013, 3, 4),
                    )
                ],
            )
        )
        module.addChild(
            model.Risk(
                title="Risk 2",
                risk_id="3",
                zodb_path="1/3",
                type="risk",
                priority="high",
                identification="no",
                action_plans=[
                    model.ActionPlan(
                        action_plan="Do something awesome",
                        planning_start=datetime.date(2013, 5, 2),
                    )
                ],
            )
        )
        module.addChild(
            model.Risk(
                title="Risk 3",
                risk_id="4",
                zodb_path="1/4",
                type="risk",
                priority="medium",
                identification="no",
                action_plans=[
                    model.ActionPlan(
                        action_plan="Do something awesome",
                        planning_start=datetime.date(2013, 4, 1),
                    )
                ],
            )
        )

        view = self.create_action_plan_timeline()
        view.context.session = self.session
        measures = view.get_measures()
        self.assertEqual(
            [risk.priority for (m, risk, measure) in measures],
            ["high", "medium", "low"],
        )


class RiskQueryTests(OiRAIntegrationTestCase):
    """Test #7547.

    A risk with evaluation method 'fixed' (i.e. skip_evaluation=true)
    and which has been identified, should appear in the final report as
    identified but without action plan.
    """

    def createData(self):
        (self.session, self.survey_session) = createSurvey()

        self.q1 = model.Module(
            **{
                "depth": 1,
                "module_id": 1,
                "has_description": True,
                "path": "001",
                "postponed": None,
                "profile_index": -1,
                "skip_children": False,
                "title": "What is the sound of one hand clapping?",
                "type": "module",
                "zodb_path": "173",
            }
        )
        self.survey_session.addChild(self.q1)

        self.mod1 = model.Module(
            **{
                "depth": 2,
                "module_id": 2,
                "has_description": True,
                "path": "001001",
                "postponed": None,
                "profile_index": 0,
                "skip_children": False,
                "title": "Stellenbosch",
                "type": "module",
                "zodb_path": "173",
            }
        )
        self.q1.addChild(self.mod1)

        self.r1 = model.Risk(
            **{
                "risk_id": 1,
                "depth": 3,
                "identification": "no",
                "action_plans": [],
                "has_description": True,
                "path": "001001001",
                "postponed": False,
                "profile_index": 0,
                "skip_children": False,
                "title": "Hands are washed",
                "type": "risk",
                "zodb_path": "173/euphorie.risk",
            }
        )
        self.mod1.addChild(self.r1)

        self.mod2 = model.Module(
            **{
                "depth": 2,
                "module_id": 3,
                "has_description": True,
                "path": "001002",
                "postponed": None,
                "profile_index": 1,
                "skip_children": False,
                "title": "Somerset West",
                "type": "module",
                "zodb_path": "173",
            }
        )
        self.q1.addChild(self.mod2)

        self.r2 = model.Risk(
            **{
                "risk_id": 1,
                "depth": 3,
                "identification": "yes",
                "action_plans": [],
                "has_description": True,
                "path": "001002001",
                "postponed": False,
                "profile_index": 1,
                "skip_children": False,
                "title": "Hands are washed",
                "type": "risk",
                "zodb_path": "173/euphorie.risk",
            }
        )
        self.mod2.addChild(self.r2)

        # self.r3 = model.Risk(**{
        #     'risk_id': 2,
        #     'depth': 3,
        #     'identification': 'no',
        #     'action_plans': [
        #         model.ActionPlan(action_plan='Add soap')
        #     ],
        #     'has_description': True,
        #     'path': u'001002001',
        #     'postponed': False,
        #     'profile_index': 1,
        #     'skip_children': False,
        #     'title': u'Hands are washed',
        #     'type': u'risk',
        #     'zodb_path': u'173/euphorie.risk'
        # })
        # self.mod2.addChild(self.r3)

    def testActionedNodes(self):
        self.createData()
        query = (
            Session()
            .query(model.SurveyTreeItem)
            .filter(model.SurveyTreeItem.session == self.survey_session)
            .order_by(model.SurveyTreeItem.path)
        )

        nodes = query.all()
        self.assertEqual(len(utils.get_actioned_nodes(nodes)), 0)

    def testUnansweredNodes(self):
        self.createData()
        self.assertEqual(len(utils.get_unanswered_nodes(self.survey_session)), 0)

    def testRiskNotPresentNodes(self):
        self.createData()
        self.assertEqual(len(utils.get_risk_not_present_nodes(self.survey_session)), 3)
