from osha.oira.testing import OiRAIntegrationTestCase
from plonetheme.nuplone.z3cform.widget import SingleRadioWidget
from z3c.form.browser.select import SelectWidget
from z3c.form.interfaces import IFieldWidget
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import zope.component


class OiRARiskTests(OiRAIntegrationTestCase):
    def _create(self, container, *args, **kwargs):
        newid = container.invokeFactory(*args, **kwargs)
        return getattr(container, newid)

    def createModule(self, algorithm="kinney", sector_name="sector"):
        country = self.portal.sectors.nl
        sector = self._create(country, "euphorie.sector", sector_name)
        surveygroup = self._create(
            sector, "euphorie.surveygroup", "group", evaluation_algorithm=algorithm
        )
        survey = self._create(surveygroup, "euphorie.survey", "survey")
        return self._create(survey, "euphorie.module", "module")

    def test_request_layers(self):
        """Test that request layers are set up correctly."""
        from osha.oira.interfaces import IOSHAContentSkinLayer
        from zope.interface import noLongerProvides

        # Given we have the IOSHAContentSkinLayer we get the AddView defined in
        # out custom package
        self.assertTrue(IOSHAContentSkinLayer.providedBy(self.request))
        self.assertEqual(
            repr(self.portal.restrictedTraverse("++add++euphorie.risk").__class__),
            "<class 'osha.oira.content.browser.risk.AddView'>",
        )

        # If we remove the IOSHAContentSkinLayer we get the AddView
        # that comes from euphorie
        noLongerProvides(self.request, IOSHAContentSkinLayer)
        self.assertEqual(
            repr(self.portal.restrictedTraverse("++add++euphorie.risk").__class__),
            "<class 'euphorie.content.browser.risk.AddView'>",
        )

    def testDynamicDescription(self):
        """#3343: Customize infoBubble description according to calculation
        method.
        """
        self.loginAsPortalOwner()
        for risk_type in ["kinney", "french"]:
            module = self.createModule(risk_type, "sector-" + risk_type)

            # Test AddForm
            form = module.unrestrictedTraverse("++add++euphorie.risk").form_instance
            form.updateFields()
            self.assertEqual(
                form.schema.get("evaluation_method").description,
                "help_evaluation_method_%s" % risk_type,
            )

            # Test EditForm
            risk = self._create(module, "euphorie.risk", "risk")
            form = risk.unrestrictedTraverse("@@edit")
            form.updateFields()
            self.assertEqual(
                form.schema.get("evaluation_method").description,
                "help_evaluation_method_%s" % risk_type,
            )
            self.portal.sectors.nl.manage_delObjects(["sector-" + risk_type])

    def testChoiceWidget(self):
        """#1537 The Choice fields must be uniform and all radio buttons."""
        self.loginAsPortalOwner()
        module = self.createModule()
        form = module.unrestrictedTraverse("++add++euphorie.risk").form_instance
        form.updateFields()

        # Test with vocabs of different lengths
        for i in [3, 5, 10]:
            v = SimpleVocabulary([SimpleTerm("%d" % k) for k in range(0, i)])
            field = form.schema.get("evaluation_method")
            field.vocabulary = v
            form.updateWidgets()

            widget = zope.component.getMultiAdapter((field, form.request), IFieldWidget)

            if i in [3, 5]:
                self.assertEqual(type(widget), SingleRadioWidget)
            else:
                self.assertEqual(type(widget), SelectWidget)
