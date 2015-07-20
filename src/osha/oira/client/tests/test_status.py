from euphorie.client import model
from euphorie.client import utils
from euphorie.client.profile import Profile
from euphorie.deployment.tests.functional import EuphorieFunctionalTestCase
from osha.oira.client import interfaces
from osha.oira.tests.base import OiRAFunctionalTestCase
from z3c.saconfig import Session
from zope import component
from zope import interface

SURVEY = \
        """<sector xmlns="http://xml.simplon.biz/euphorie/survey/1.0">
             <title>ICT</title>
             <survey>
              <title>Software development</title>
              <module optional="no">
                <title>Module one</title>
                <description>Quick description</description>
                 <risk type="policy">
                   <title>New hires are not aware of design patterns.</title>
                   <description>&lt;p&gt;Every developer should know about them..&lt;/p&gt;</description>
                   <evaluation-method>direct</evaluation-method>
                   <image caption="Key image" content-type="image/gif">R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAEALAAAAAABAAEAAAIBTAA7</image>
                 </risk>
              </module>

              <title>Software development</title>
              <profile-question>
                <title>Profile one</title>
                <question>List all your departments:</question>
                <description/>
                <risk type="policy">
                  <title>New hires are not aware of design patterns.</title>
                  <description>&lt;p&gt;Every developer should know about them..&lt;/p&gt;</description>
                  <evaluation-method>direct</evaluation-method>
                </risk>
              </profile-question>
            </survey>
          </sector>"""


def addSurvey(portal, xml_survey):
    """Add a survey to the portal. This function requires that you are already
    loggin in as portal owner."""
    from euphorie.content import upload
    from euphorie.client import publish
    importer = upload.SectorImporter(portal.sectors.nl)
    sector = importer(xml_survey, None, None, None, u"test import")
    survey = sector.values()[0]["test-import"]
    publisher = publish.PublishSurvey(survey, portal.REQUEST)
    publisher.publish()


class SurveySessionTests(EuphorieFunctionalTestCase):

    def createSurveySession(self):
        self.sqlsession = Session()
        account = model.Account(loginname=u"jane", password=u"secret")
        self.sqlsession.add(account)
        self.session = model.SurveySession(
            title=u"Session",
            zodb_path="nl/dining/survey", account=account)
        self.sqlsession.add(self.session)
        self.sqlsession.flush()
        return self.session

    def testStatusView(self):
        self.loginAsPortalOwner()
        addSurvey(self.portal, SURVEY)
        survey = self.portal.client.nl["ict"]["software-development"]
        request = self.portal.REQUEST
        request.survey = survey
        request.other["euphorie.session"] = self.createSurveySession()
        utils.setRequest(request)
        interface.alsoProvides(request, interfaces.IOSHAClientSkinLayer)
        view = component.getMultiAdapter(
            (survey, request), name="status")
        status = view.getStatus()
