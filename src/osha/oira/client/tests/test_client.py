from osha.oira.testing import OiRAFunctionalTestCase


class ClientTest(OiRAFunctionalTestCase):
    def testTraverser(self):
        """Test the ClientPublishTraverser in osha.oira/client.py."""
        from ..interfaces import IOSHAClientSkinLayer
        from euphorie.client.utils import locals

        browser = self.get_browser()
        browser.open(self.portal.client.absolute_url())
        self.assertEqual(IOSHAClientSkinLayer.providedBy(locals.request), True)
