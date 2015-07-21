from euphorie.client import model
from euphorie.client import utils
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

def createSurveySession():
    sqlsession = Session()
    account = model.Account(loginname=u"jane", password=u"secret")
    sqlsession.add(account)
    session = model.SurveySession(
        title=u"Session",
        zodb_path="ict/software-development", account=account)
    sqlsession.add(session)
    sqlsession.flush()
    return session

class SurveySessionTests(OiRAFunctionalTestCase):

    def testStatusView(self):
        self.loginAsPortalOwner()
        addSurvey(self.portal, SURVEY)
        survey = self.portal.client.nl["ict"]["software-development"]
        request = self.portal.REQUEST
        request.survey = survey
        request.other["euphorie.session"] = createSurveySession()
        utils.setRequest(request)
        interface.alsoProvides(request, interfaces.IOSHAClientSkinLayer)
        view = component.getMultiAdapter(
            (survey, request), name="status")

        def getModules():
            return {
                u'001001': {
                    'ok': 0,
                    'path': u'001001',
                    'postponed': 0,
                    'risk_with_measures': 0,
                    'risk_without_measures': 0,
                    'title': u'Shops are clean - Somerset West',
                    'todo': 9,
                    'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/1/1'
                }
            }

        def getRisks(dummy):
            return [
                {   'title': u"Le conducteur est-il prot\xe9g\xe9 des autres v\xe9hicules lorsqu'il circule au sol ?",
                    'priority': u'medium',
                    'identification': u'no',
                    'path': u'001001001',
                    'module_path': u'001001',
                    'postponed': False, 'id': 324781
                },
                {   'title': u"Le conducteur effectue-t-il toutes ses man\u0153uvres d'accroche/d\xe9croche depuis le sol ?",
                    'priority': u'high',
                    'identification': u'no',
                    'path': u'001001002',
                    'module_path': u'001001',
                    'postponed': False, 'id': 324780
                },
                {
                    'title': u'Le conducteur descend-il de sa cabine en utilisant les marches ?',
                    'priority': u'high',
                    'identification': u'yes',
                    'path': u'001001003',
                    'module_path': u'001001',
                    'postponed': False, 'id': 324772
                }
            ]

        view.getModules = getModules
        view.getRisks = getRisks
        view.getStatus()
        self.assertEquals(view.status[0]['title'], u'Shops are clean - Somerset West');
        self.assertEquals(view.status[0]['risk_without_measures'], 2);
        self.assertEquals(view.status[0]['risk_with_measures'], 0);
        self.assertEquals(view.status[0]['postponed'], 0);
        self.assertEquals(view.status[0]['todo'], 0);
        self.assertEquals(view.status[0]['ok'], 1);
        self.assertEquals(view.percentage_ok, 33);
