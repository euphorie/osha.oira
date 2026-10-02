from osha.oira.testing import OIRA_INTEGRATION_TESTING
from plone import api

import unittest


class TestOshaOiraSetup(unittest.TestCase):
    layer = OIRA_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_default_token_is_set(self):
        """Test that the default token is set in the registry."""
        token = api.portal.get_registry_record("osha.oira.mailings.token")
        self.assertIsInstance(token, str)
        self.assertEqual(len(token), 32)  # UUID4 hex string length
