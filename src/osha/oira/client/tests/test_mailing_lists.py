from euphorie.client.browser import publish
from euphorie.client.interfaces import IClientSkinLayer
from euphorie.client.model import Account
from euphorie.client.model import SurveySession
from euphorie.client.tests.utils import addSurvey
from euphorie.content.browser import upload
from euphorie.content.tests.utils import BASIC_SURVEY
from osha.oira.client.browser.client import GroupToAddresses
from osha.oira.client.browser.client import MailingListsJson
from osha.oira.client.model import NewsletterSubscription
from osha.oira.testing import OiRAIntegrationTestCase
from plone import api
from unittest import mock
from z3c.saconfig import Session
from zope.interface import alsoProvides


class TestMailingLists(OiRAIntegrationTestCase):
    def setUp(self):
        super().setUp()
        survey = """<sector xmlns="http://xml.simplon.biz/euphorie/survey/1.0">
                      <title>Test</title>
                      <survey>
                        <title>Software development</title>
                        <language>fr</language>
                        </survey>
                    </sector>"""
        survey2 = """<sector xmlns="http://xml.simplon.biz/euphorie/survey/1.0">
                      <title>Another Test</title>
                      <survey>
                        <title>Audio Production</title>
                        <language>fr</language>
                        </survey>
                    </sector>"""

        with api.env.adopt_user("admin"):
            addSurvey(self.portal, BASIC_SURVEY)
            addSurvey(self.portal, survey)

            importer = upload.SectorImporter(self.portal.sectors.de)
            sector = importer(survey2, None, None, None, "test import")
            survey = sector.values()[0]["test-import"]
            publisher = publish.PublishSurvey(survey, self.portal.REQUEST)
            publisher.publish()

            with mock.patch.object(self.portal.acl_users.euphorie, "REQUEST"):
                self.user = api.user.create(
                    username="ignaz", email="ignaz@example.org", password="Secret123!"
                )
            api.user.grant_roles(
                username="ignaz", obj=self.portal.sectors.nl, roles=["CountryManager"]
            )

            self.portal.portal_catalog.manage_reindexIndex("managerRolesAndUsers")

    def test_mailing_lists(self):
        request = self.request.clone()
        request.form = {"user_id": "admin"}
        with mock.patch.object(
            MailingListsJson,
            "addresses_view",
            return_value=GroupToAddresses(context=self.portal.client, request=request),
        ):
            view = MailingListsJson(context=self.portal.client, request=request)
            results = view.results
        self.assertIn(
            {"id": "general|QWxsIHVzZXJz", "text": "All users [0 subscribers]"}, results
        )
        self.assertIn(
            {
                "id": "nl-nl|VGhlIE5ldGhlcmxhbmRzIChubCk=",
                "text": "The Netherlands (nl) [0 subscribers]",
            },
            results,
        )
        self.assertIn(
            {
                "id": "nl-fr|VGhlIE5ldGhlcmxhbmRzIChmcik=",
                "text": "The Netherlands (fr) [0 subscribers]",
            },
            results,
        )
        self.assertIn(
            {
                "id": "nl/ict/software-development|U29mdHdhcmUgZGV2ZWxvcG1lbnQ=",
                "text": (
                    "Software development (nl/ict/software-development) [0 subscribers]"
                ),
            },
            results,
        )

    def test_mailing_lists_batching(self):
        request = self.request.clone()
        request.form = {"user_id": "ignaz", "page_limit": "2"}
        with mock.patch.object(
            MailingListsJson,
            "addresses_view",
            return_value=GroupToAddresses(context=self.portal.client, request=request),
        ):
            view = MailingListsJson(context=self.portal.client, request=request)
            results = view.results

        self.assertEqual(len(results), 2)
        self.assertEqual(
            results[0],
            {
                "id": "nl/ict/software-development|U29mdHdhcmUgZGV2ZWxvcG1lbnQ=",
                "text": "Software development (nl/ict/software-development) [0 subscribers]",  # noqa: E501
            },
        )
        self.assertEqual(
            results[1],
            {
                "id": "nl/test/software-development|U29mdHdhcmUgZGV2ZWxvcG1lbnQ=",
                "text": "Software development (nl/test/software-development) [0 subscribers]",  # noqa: E501
            },
        )

        request.form = {"user_id": "ignaz", "page_limit": "2", "page": "2"}
        with mock.patch.object(
            MailingListsJson,
            "addresses_view",
            return_value=GroupToAddresses(context=self.portal.client, request=request),
        ):
            view = MailingListsJson(context=self.portal.client, request=request)
            results = view.results

        self.assertEqual(len(results), 3)
        self.assertEqual(
            results[0],
            {
                "id": "nl-fr|VGhlIE5ldGhlcmxhbmRzIChmcik=",
                "text": "The Netherlands (fr) [0 subscribers]",
            },
        )
        self.assertEqual(
            results[1],
            {
                "id": "nl-nl|VGhlIE5ldGhlcmxhbmRzIChubCk=",
                "text": "The Netherlands (nl) [0 subscribers]",
            },
        )
        self.assertEqual(
            results[2],
            {
                "id": "nl-managers|VGhlIE5ldGhlcmxhbmRzIGNvdW50cnkgbWFuYWdlcnM=",
                "text": "The Netherlands country managers [0 subscribers]",
            },
        )

    def test_group_to_addresses(self):
        user = Account(loginname="leni@example.nl", password="secret")
        Session.add(user)
        alsoProvides(self.request, IClientSkinLayer)
        with api.env.adopt_user("leni@example.nl"):
            survey_session = SurveySession(
                id=1,
                title="Software",
                zodb_path="nl/ict/software-development",
                account=user,
            )
        Session.add(survey_session)
        Session.add(
            NewsletterSubscription(
                account_id=user.id,
                zodb_path="nl",
            )
        )
        Session.add(
            NewsletterSubscription(
                account_id=user.id,
                zodb_path="nl/ict/software-development",
            )
        )
        Session.flush()

        request = self.request.clone()
        request.form = {"groups": "nl-nl"}
        view = GroupToAddresses(context=self.portal.client, request=request)
        results = view.results
        self.assertIn("leni@example.nl", results)

        request = self.request.clone()
        request.form = {"groups": "nl-fr"}
        view = GroupToAddresses(context=self.portal.client, request=request)
        results = view.results
        self.assertNotIn("leni@example.nl", results)

        request = self.request.clone()
        request.form = {"groups": "nl/ict/software-development"}
        view = GroupToAddresses(context=self.portal.client, request=request)
        results = view.results
        self.assertIn("leni@example.nl", results)
