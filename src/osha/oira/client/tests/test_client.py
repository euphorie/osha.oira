from osha.oira.tests.base import OiRAFunctionalTestCase


class ClientTest(OiRAFunctionalTestCase):
    def testTraverser(self):
        """Test the ClientPublishTraverser in osha.oira/client.py"""
        from ..interfaces import IOSHAClientSkinLayer
        from euphorie.client.utils import locals
        from Products.Five.testbrowser import Browser

        browser = Browser()
        browser.open(self.portal.client.absolute_url())
        self.assertEquals(IOSHAClientSkinLayer.providedBy(locals.request), True)
