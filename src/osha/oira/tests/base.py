import os.path
from zope.component import getUtility
from z3c.saconfig import Session
from z3c.appconfig.interfaces import IAppConfig
from Testing.ZopeTestCase import installProduct
from collective.testcaselayer import ptc
from Products.PloneTestCase import PloneTestCase
from euphorie.deployment.tests.functional import EuphorieFunctionalTestCase
from euphorie.client import model

PloneTestCase.setupPloneSite()

# This should in theory work in the afterSetUp() method, but it does not work there
installProduct("membrane")

TEST_INI = os.path.join(os.path.dirname(__file__), "test.ini")


class OiRATestLayer(ptc.BasePTCLayer):
    def afterSetUp(self):
        from Testing.ZopeTestCase import installPackage
        from euphorie.client import tests
        import euphorie.deployment
        import osha.oira

        self.loadZCML("configure.zcml", package=euphorie.deployment)
        self.loadZCML("overrides.zcml", package=euphorie.deployment)
        self.loadZCML("configure.zcml", package=tests)
        self.loadZCML("configure.zcml", package=osha.oira)

        installPackage("plone.uuid")
        installPackage("collective.indexing")
        installPackage("plone.app.dexterity")
        installPackage("plone.app.folder")
        installPackage("euphorie.content")
        installPackage("euphorie.client")
        installPackage("euphorie.deployment")
        installPackage("plonetheme.nuplone")
        installPackage("osha.oira")

        self.addProduct("euphorie.deployment")
        self.addProduct("osha.oira")

        model.metadata.create_all(Session.bind, checkfirst=True)
        appconfig = getUtility(IAppConfig)
        appconfig.loadConfig(TEST_INI, clear=True)

    def beforeTearDown(self):
        Session.remove()
        model.metadata.drop_all(Session.bind)

    # XXX testSetUp and testTearDown should not be neceesary, but it seems
    # SQL data is not correctly cleared at the end of a test method run,
    # even if testTearDown does an explicit transaction.abort()
    def testSetUp(self):
        model.metadata.create_all(Session.bind, checkfirst=True)

    def testTearDown(self):
        Session.remove()
        model.metadata.drop_all(Session.bind)

OiRALayer = OiRATestLayer([ptc.ptc_layer])


class OiRATestCase(PloneTestCase.PloneTestCase):
    layer = OiRALayer


class OiRAFunctionalTestCase(EuphorieFunctionalTestCase):
    layer = OiRATestLayer
