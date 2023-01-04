from euphorie.testing import EuphorieFixture
from euphorie.testing import EuphorieFunctionalTestCase
from euphorie.testing import EuphorieIntegrationTestCase
from osha.oira.client.interfaces import IClientSkinLayer
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.testing import z2


class OiRAFixture(EuphorieFixture):
    def setUpZope(self, app, configurationContext):
        super().setUpZope(app, configurationContext)
        import osha.oira

        self.loadZCML(
            name="configure.zcml",
            package=osha.oira,
            context=configurationContext,
        )

    def setUpPloneSite(self, portal):
        super().setUpPloneSite(portal)
        self.applyProfile(portal, "osha.oira:default")


OIRA_FIXTURE = OiRAFixture()
OIRA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(OIRA_FIXTURE,), name="osha.oira:Integration"
)

OIRA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(OIRA_FIXTURE,),
    name="osha.oira:Functional",
)

OIRA_SUITE_ROBOT = FunctionalTesting(
    bases=(OIRA_FIXTURE, AUTOLOGIN_LIBRARY_FIXTURE, z2.ZSERVER_FIXTURE),
    name="OIRA_SUITE_ROBOT",
)


class OiRAIntegrationTestCase(EuphorieIntegrationTestCase):
    layer = OIRA_INTEGRATION_TESTING
    request_layer = IClientSkinLayer


class OiRAFunctionalTestCase(EuphorieFunctionalTestCase):
    layer = OIRA_FUNCTIONAL_TESTING
    request_layer = IClientSkinLayer
