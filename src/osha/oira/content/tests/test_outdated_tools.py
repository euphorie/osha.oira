# coding=utf-8
from euphorie.client import publish
from euphorie.client.tests.utils import MockMailFixture
from euphorie.content.tests.utils import BASIC_SURVEY
from euphorie.content.tests.utils import _create
from euphorie.content.tests.utils import addSurvey
from euphorie.content.tests.utils import createSector
from osha.oira.tests.base import OiRATestCase
from plone import api

import mock


class OutdatedToolsTests(OiRATestCase):

    def afterSetUp(self):
        super(OutdatedToolsTests, self).afterSetUp()
        self.loginAsPortalOwner()
        sector = createSector(self.portal)
        sector.contact_name = u'Sectör NL'
        sector.contact_email = u'sect@r.nl'

        survey = addSurvey(sector, BASIC_SURVEY)
        nl = sector.aq_parent
        # User invalid emails to skip an event handler
        nl.invokeFactory(
            'euphorie.countrymanager',
            'nl-cm-1',
            title=u'Country Mänager 1',
            contact_email='invalid_email1',
        )
        nl.invokeFactory(
            'euphorie.countrymanager',
            'nl-cm-2',
            title=u'Country Mänager 2',
            contact_email='invalid_email2',
        )

        outdated_client_survey = publish.CopyToClient(survey)
        # Index the object with an older modified date
        outdated_client_survey.reindexObject()
        outdated_client_survey.setModificationDate('2013')
        outdated_client_survey.reindexObject(idxs=['modified'])

        sector_de = createSector(self.portal, id='sector_de', country='de')
        survey_de = addSurvey(sector_de, BASIC_SURVEY)
        client_survey_de = publish.CopyToClient(survey_de)
        self.mail_fixture = MockMailFixture()
        self.portal.email_from_address = "from@example.com"
        self.portal.email_from_name = "Euphorie website"

    def test_outdated_tool_paths(self):
        view = self.portal.restrictedTraverse('@@outdated-tools-view')
        paths = view.get_outdated_tool_paths()
        self.assertTrue('/plone/sectors/nl/sector/test-survey' in paths)
        self.assertTrue('/plone/sectors/de/sector/test-survey' not in paths)

    def test_send_sector_manager_notifications(self):
        view = self.portal.restrictedTraverse('@@outdated-tools-view')
        outdated_tool_paths = view.get_outdated_tool_paths()
        view.send_sector_manager_notifications(outdated_tool_paths)
        self.assertEqual(len(self.mail_fixture.storage), 1)
        email = self.mail_fixture.storage[0][0][0].as_string()
        self.assertTrue('/sectors/nl/sector/test-survey' in email)
        # To: Sectör NL <sect@r.nl>
        self.assertTrue(
            'To: =?utf-8?b?U2VjdMO2ciBOTCA8c2VjdEByLm5sPg==?=' in email)

    def test_send_country_manager_notifications(self):
        view = self.portal.restrictedTraverse('@@outdated-tools-view')
        outdated_tool_paths = view.get_outdated_tool_paths()
        view.send_country_manager_notifications(outdated_tool_paths)
        self.assertEqual(len(self.mail_fixture.storage), 2)
        email = self.mail_fixture.storage[0][0][0].as_string()
        self.assertTrue('/sectors/nl/sector/test-survey' in email)
        # To: Country Mänager 1 <invalid_email1>
        self.assertTrue(
            'To: =?utf-8?q?Country_M=C3=A4nager_1_=3Cinvalid' in email)
