from plone import api
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from zope.configuration import xmlconfig


class OiRAFixture(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        z2.installProduct(app, 'Products.membrane')
        z2.installProduct(app, 'Products.statusmessages')
        import Products.statusmessages
        xmlconfig.file('configure.zcml',
                       Products.statusmessages,
                       context=configurationContext)
        import Products.membrane
        xmlconfig.file('configure.zcml',
                       Products.membrane,
                       context=configurationContext)
        import euphorie.client.tests
        xmlconfig.file("configure.zcml",
                       euphorie.client.tests,
                       context=configurationContext)
        import osha.oira
        xmlconfig.file('configure.zcml',
                       osha.oira,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        wftool = api.portal.get_tool(name='portal_workflow')
        wftool.setDefaultChain('plone_workflow')
        applyProfile(portal, 'euphorie.content:default')
        applyProfile(portal, 'euphorie.client:default')
        applyProfile(portal, 'euphorie.deployment:default')
        applyProfile(portal, 'osha.oira:default')

OIRA_FIXTURE = OiRAFixture()
OIRA_INTEGRATION_TESTING = \
    IntegrationTesting(
        bases=(OIRA_FIXTURE,),
        name="osha.oira:Integration"
    )

OIRA_SUITE_ROBOT = FunctionalTesting(
    bases=(OIRA_FIXTURE,
           AUTOLOGIN_LIBRARY_FIXTURE,
           z2.ZSERVER_FIXTURE),
    name="OIRA_SUITE_ROBOT")
