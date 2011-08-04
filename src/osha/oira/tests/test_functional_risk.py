from zope.interface import alsoProvides
from osha.oira.tests.base import OiRATestCase
from osha.oira import interfaces

class RiskTest(OiRATestCase):

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
            alsoProvides(self.portal.REQUEST, interfaces.IOSHAContentSkinLayer)

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

