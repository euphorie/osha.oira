# coding=utf-8

from z3c.form.interfaces import IFieldWidget
from z3c.form.browser.select import SelectWidget
import zope.component
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm
from zope.interface import alsoProvides

from Products.Five.testbrowser import Browser

from plonetheme.nuplone.z3cform.widget import SingleRadioWidget

from euphorie.client.tests.utils import addSurvey
from euphorie.client.tests.utils import registerUserInClient

from osha.oira.tests.base import OiRATestCase
from osha.oira.tests.base import OiRAFunctionalTestCase
from osha.oira import interfaces

class OiRARiskTests(OiRATestCase):

    def _create(self, container, *args, **kwargs):
        newid = container.invokeFactory(*args, **kwargs)
        return getattr(container, newid)

    def createModule(self, algorithm='kinney'):
        country = self.portal.sectors.nl
        sector = self._create(country, "euphorie.sector", "sector")
        surveygroup = self._create(
                                sector, 
                                "euphorie.surveygroup", 
                                "group",
                                evaluation_algorithm=algorithm)
        survey = self._create(surveygroup, "euphorie.survey", "survey")
        return self._create(survey, "euphorie.module", "module")

    def createRisk(self, algorithm='kinney'):
        module = self.createModule(algorithm)
        return self._create(module, "euphorie.risk", "risk")

    def testDynamicDescription(self):
        """ #3343: Customize infoBubble description according to calculation
            method.
        """
        self.loginAsPortalOwner()
        for risk_type in ['kinney', 'french']:
            module = self.createModule(risk_type)
            # Merely installing the OiRA skin doesn't set it's layer on the
            # request. This happens during IBeforeTraverseEvent, so we have to do 
            # here manually
            alsoProvides(self.portal.REQUEST, interfaces.IOSHAContentFormLayer)

            # Test AddForm
            form = module.unrestrictedTraverse('++add++euphorie.risk').form_instance
            form.updateFields()
            self.assertEqual(
                    form.schema.get('evaluation_method').description, 
                    'help_evaluation_method_%s' % risk_type
                    )

            # Test EditForm
            risk = self._create(module, "euphorie.risk", "risk")
            form = risk.unrestrictedTraverse('@@edit').form_instance
            form.updateFields()
            self.assertEqual(
                    form.schema.get('evaluation_method').description, 
                    'help_evaluation_method_%s' % risk_type
                    )
            self.portal.sectors.nl.manage_delObjects(['sector'])


    def testChoiceWidget(self):
        """ #1537 The Choice fields must be uniform and all radio buttons.
        """
        self.loginAsPortalOwner()
        module = self.createModule()
        alsoProvides(self.portal.REQUEST, interfaces.IOSHAContentFormLayer)
        form = module.unrestrictedTraverse('++add++euphorie.risk').form_instance
        form.updateFields()

        # Test with vocabs of different lengths
        for i in [3, 5, 10]:
            v = SimpleVocabulary([SimpleTerm("%d" % k) for k in range(0, i)])
            field = form.schema.get('evaluation_method')
            field.vocabulary = v
            form.updateWidgets()

            widget = zope.component.getMultiAdapter(
                (field, form.request), IFieldWidget)

            if i in [3, 5]:
                self.assertEqual(type(widget), SingleRadioWidget)
            else:
                self.assertEqual(type(widget), SelectWidget)


class EuphorieRiskTests(OiRAFunctionalTestCase):

    def testShowFrenchEvaluation(self):
        from euphorie.content.tests.utils import BASIC_SURVEY
        # Test for http://code.simplon.biz/tracker/tno-euphorie/ticket/150
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser=Browser()
        survey=self.portal.client.nl["ict"]["software-development"]
        survey.evaluation_algorithm=u"french"
        survey["1"]["2"].type="risk"
        browser.open(survey.absolute_url())
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value=u"Sessiøn".encode("utf-8")
        browser.getControl(name="next", index=1).click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Identify the risk
        browser.getControl("next").click()
        browser.getControl(name="answer").value=["no"]
        browser.getControl("next").click()
        # Move on to the risk's action plan form
        browser.getLink("Run evaluation").click()
        browser.handleErrors=False
        browser.getLink("Next").click()
        # Verify number of options
        self.assertEqual(len(browser.getControl(name="frequency:int").controls), 4)
        self.assertEqual(len(browser.getControl(name="severity:int").controls), 4)
        # Enter some digits
        browser.getControl(name="frequency:int").value=["7"]
        browser.getControl(name="severity:int").value=["10"]
        browser.getControl("next").click()
        # Verify the result
        browser.open(
                "http://nohost/plone/client/nl/ict/software-development/actionplan/1/1")
        self.assertEqual(browser.getControl(name="priority").value, ["high"])

    def testPreventEarlyDate(self):
        from euphorie.content.tests.utils import BASIC_SURVEY
        # Test for http://code.simplon.biz/tracker/tno-euphorie/ticket/150
        self.loginAsPortalOwner()
        addSurvey(self.portal, BASIC_SURVEY)
        browser=Browser()
        survey_url=self.portal.client.nl["ict"]["software-development"].absolute_url()
        browser.open(survey_url)
        registerUserInClient(browser)
        # Create a new survey session
        browser.getControl(name="title:utf8:ustring").value=u"Sessiøn".encode("utf-8")
        browser.getControl(name="next", index=1).click()
        # Start the survey
        browser.getForm().submit()
        browser.getLink("Start Risk Identification").click()
        # Identify the risk
        browser.getControl("next").click()
        browser.getControl(name="answer").value=["no"]
        browser.getControl("next").click()
        # Move on to the risk's action plan form
        browser.getLink("Go to action plan").click()
        browser.getLink("Create action plan").click()
        browser.getLink("Next").click()
        # Try an early year
        browser.getControl(name="measure.action_plan:utf8:ustring:records").value="Do something awesome"
        browser.getControl(name="measure.planning_start_day:records").value="1"
        browser.getControl(name="measure.planning_start_month:records").value=["2"]
        browser.getControl(name="measure.planning_start_year:records").value="3"
        browser.getControl("next").click()
        self.assertEqual(browser.url,
                "http://nohost/plone/client/nl/ict/software-development/actionplan/1/1")
        self.assertTrue("Please enter a valid year after 1900" in browser.contents)

