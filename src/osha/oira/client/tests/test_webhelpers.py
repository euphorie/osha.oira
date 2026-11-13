from osha.oira.client.browser.webhelpers import _matomo_unique_key
from osha.oira.client.browser.webhelpers import MATOMO_JS
from osha.oira.client.interfaces import IOSHAClientSkinLayer
from osha.oira.testing import OiRAFunctionalTestCase
from plone import api
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.interface import alsoProvides

import re
import transaction


class TestMatomoIntegration(OiRAFunctionalTestCase):
    def setUp(self):
        super().setUp()
        alsoProvides(self.request, IOSHAClientSkinLayer)

    def set_webstats_js(self, value):
        # plone.api refuses None, so write to the registry directly.
        getUtility(IRegistry)["plone.webstats_js"] = value

    def get_webstats_js(self):
        view = api.content.get_view(
            "webhelpers", context=self.portal.client, request=self.request
        )
        return view.get_webstats_js()

    def test_matomo_js_file_exists(self):
        self.assertTrue(MATOMO_JS.is_file(), f"{MATOMO_JS} does not exist.")

    def test_get_webstats_js_renders_script_tag(self):
        self.set_webstats_js(None)
        webstats_js = self.get_webstats_js()
        self.assertIn(
            f"{self.portal.absolute_url()}/{_matomo_unique_key()}"
            "/++resource++osha.oira.client/matomo-integration.js",
            webstats_js,
        )

    def test_get_webstats_js_keeps_registry_value(self):
        self.set_webstats_js("<script>/* custom */</script>")
        webstats_js = self.get_webstats_js()
        self.assertTrue(webstats_js.startswith("<script>/* custom */</script>"))
        self.assertIn("matomo-integration.js", webstats_js)

    def test_matomo_js_is_served(self):
        """The rendered script URL must resolve to the integration script."""
        self.set_webstats_js(None)
        src = re.search(r'src="([^"]+)"', self.get_webstats_js()).group(1)
        transaction.commit()
        browser = self.get_browser()
        browser.open(src)
        self.assertEqual(browser.contents.strip(), MATOMO_JS.read_bytes().strip())
