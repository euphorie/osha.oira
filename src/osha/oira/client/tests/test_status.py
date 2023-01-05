from euphorie.client import model
from euphorie.client import utils
from osha.oira.client import interfaces
from osha.oira.testing import OiRAFunctionalTestCase
from z3c.saconfig import Session
from zope import component
from zope import interface

import unittest


SURVEY = """<sector xmlns="http://xml.simplon.biz/euphorie/survey/1.0">
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
          </sector>"""  # noqa: E501


def addSurvey(portal, xml_survey):
    """Add a survey to the portal.

    This function requires that you are already loggin in as portal
    owner.
    """
    from euphorie.client.browser import publish
    from euphorie.content.browser import upload

    importer = upload.SectorImporter(portal.sectors.nl)
    sector = importer(xml_survey, None, None, None, "test import")
    survey = sector.values()[0]["test-import"]
    publisher = publish.PublishSurvey(survey, portal.REQUEST)
    publisher.publish()


def createSurveySession():
    sqlsession = Session()
    account = model.Account(loginname="jane", password="secret")
    sqlsession.add(account)
    session = model.SurveySession(
        title="Session", zodb_path="ict/software-development", account=account
    )
    sqlsession.add(session)
    sqlsession.flush()
    return session


class SurveySessionTests(OiRAFunctionalTestCase):
    def setUp(self):
        super().setUp()
        self.loginAsPortalOwner()
        addSurvey(self.portal, SURVEY)
        self.survey = self.portal.client.nl["ict"]["software-development"]

        class DummyObj:
            problem_description = "A Tricky Problem"

        self.survey.restrictedTraverse = lambda path: DummyObj()
        self.request = self.portal.REQUEST
        self.request.survey = self.survey
        self.request.other["euphorie.session"] = createSurveySession()
        utils.setRequest(self.request)
        interface.alsoProvides(self.request, interfaces.IOSHAClientSkinLayer)

        self.module = model.Module(
            zodb_path="1",
            path="001001",
            title="Shops are clean - Somerset West",
        )
        self.risk1 = model.Risk(
            zodb_path="504/277/444",
            risk_id="1",
            title="Le conducteur est-il prot\xe9g\xe9 des autres v\xe9hicules lorsqu'il circule au sol ?",  # noqa: E501
            priority="medium",
            identification="no",
            path="001001001",
        )
        self.risk2 = model.Risk(
            zodb_path="504/277/444",
            risk_id="1",
            title="Le conducteur effectue-t-il toutes ses man\u0153uvres d'accroche/d\xe9croche depuis le sol ?",  # noqa: E501
            priority="high",
            identification="no",
            path="001001002",
        )
        self.risk3_no = model.Risk(
            zodb_path="504/277/385",
            risk_id="1",
            title="Le conducteur descend-il de sa cabine en utilisant les marches ?",
            priority="low",
            identification="no",
            path="001001003",
        )
        self.risk3_yes = model.Risk(
            zodb_path="504/277/385",
            risk_id="1",
            title="Le conducteur descend-il de sa cabine en utilisant les marches ?",
            priority="low",
            identification="yes",
            path="001001003",
        )
        self.risk4 = model.Risk(
            zodb_path="504/277/383",
            risk_id="1",
            title="Un autre risque ?",
            priority="medium",
            identification=None,
            path="001001004",
        )
        self.risk5 = model.Risk(
            zodb_path="504/277/444",
            risk_id="1",
            title="Encore un autre risque ?",
            priority="low",
            identification=None,
            path="001001005",
            postponed=True,
        )

    def _getModules(self):
        return {
            "001001": {
                "ok": 0,
                "path": "001001",
                "postponed": 0,
                "risk_with_measures": 0,
                "risk_without_measures": 0,
                "title": "Shops are clean - Somerset West",
                "todo": 0,
                "url": "http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/1/1",  # noqa: E501
            }
        }

    def _getRisks(self, list_of_modules=None):
        if self._testMethodName == "testStatusView":
            risk3 = self.risk3_yes
        else:
            risk3 = self.risk3_no
        return [
            (self.module, self.risk1),
            (self.module, self.risk2),
            (self.module, risk3),
            (self.module, self.risk4),
            (self.module, self.risk5),
        ]

    @unittest.skip("self.survey not a ITraversedSurveySession")
    def testStatusView(self):
        view = component.getMultiAdapter((self.survey, self.request), name="status")

        view.getModules = self._getModules
        view.getRisks = self._getRisks
        view.tocdata = {
            "001001": {
                "path": "001001",
                "title": "Shops are clean - Somerset West",
                "locations": [],
                "number": 1,
            }
        }
        view.getStatus()
        self.assertEqual(view.status[0]["title"], "Shops are clean - Somerset West")
        self.assertEqual(view.status[0]["risk_without_measures"], 2)
        self.assertEqual(view.status[0]["risk_with_measures"], 0)
        self.assertEqual(view.status[0]["postponed"], 1)
        self.assertEqual(view.status[0]["todo"], 1)
        self.assertEqual(view.status[0]["ok"], 1)
        self.assertEqual(view.percentage_ok, 20)
        self.assertEqual(len(view.risks_by_status["001001"]["present"]["high"]), 1)
