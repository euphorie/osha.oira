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
            return {u'010': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'Activit\xe9s administratives',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/10',
                'path': u'010',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0},
            u'002': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'Attelage',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/2',
                'path': u'002',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0},
            u'012': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'Other risks',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/12',
                'path': u'012',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            },
            u'003': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'Mise \xe0 quai',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/3',
                'path': u'003',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            },
            u'011001': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'What is the sound of one hand clapping? - Somerset West',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/11/1',
                'path': u'011001',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            },
            u'011002': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'What is the sound of one hand clapping? - Stellenbosch',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/11/2',
                'path': u'011002',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            },
            u'007': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'Conduite - Circulation routi\xe8re',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/7',
                'path': u'007',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            },
            u'006': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'D\xe9part du quai',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/6',
                'path': u'006',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            },
            u'005': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'Arrimage',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/5',
                'path': u'005',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            },
            u'004': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'Chargement / d\xe9chargement',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/4',
                'path': u'004',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            },
            u'009': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'Maintenance de 1er niveau',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/9',
                'path': u'009',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            },
            u'008': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'Arriv\xe9e chez le client',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/8',
                'path': u'008',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            },
            u'001': {
                'risk_without_measures': 0,
                'ok': 0,
                'title': u'Prise de v\xe9hicule',
                'url': u'http://oira:4080/Plone2/client/fr/transportroutier/transporoutier-2-parametres/identification/1',
                'path': u'001',
                'risk_with_measures': 0,
                'postponed': 0,
                'todo': 0
            }
        }

        def getRisks():
            return [{
                'title': u"Le v\xe9hicule dispose-t-il d'un syst\xe8me d'ouverture des portes peu sollicitant pour les bras ?", 'priority': u'low',
                'identification': None, 'path': u'003002002',
                'module_path': u'003',
                'postponed': True, 'id': 324795},
                {'title': u"A l'ouverture des portes arri\xe8res, le conducteur est-il prot\xe9g\xe9 de la chute de marchandises ?", 'priority': u'low',
                'identification': None, 'path': u'003002001',
                'module_path': u'003',
                'postponed': False, 'id': 324794},
                {'title': u'Le conducteur maitrise-t-il les r\xe8gles de mise \xe0 quai du lieu de chargement ?',
                'priority': u'low',
                'identification': None, 'path': u'003001002',
                'module_path': u'003',
                'postponed': False, 'id': 324792},
                {'title': u'Le conducteur reste-t-il dans la cabine pour se mettre \xe0 quai ?',
                'priority': u'low',
                'identification': None, 'path': u'003001001',
                'module_path': u'003',
                'postponed': False, 'id': 324791},
                {'title': u'Hands are washed',
                'priority': u'high',
                'identification': None, 'path': u'011002001',
                'module_path': u'011002',
                'postponed': False, 'id': 324846},
                {'title': u'Hands are washed',
                'priority': u'high',
                'identification': None, 'path': u'011001001',
                'module_path': u'011001',
                'postponed': False, 'id': 324844},
                {'title': u"Le conducteur est-il \xe0 l'aise avec les t\xe2ches administratives \xe0 remplir ?", 'priority': u'low',
                'identification': None, 'path': u'010001001',
                'module_path': u'010',
                'postponed': False, 'id': 324841},
                {'title': u'Le conducteur sait-il effectuer une maitenance de 1er niveau sur son v\xe9hicule ?',
                'priority': u'low',
                'identification': None, 'path': u'009001',
                'module_path': u'009',
                'postponed': False, 'id': 324838},
                {'title': u'Le conducteur connait-il le protocole de s\xe9curit\xe9 \xe9tabli avec le client \xe0 livrer ?',
                'priority': u'low',
                'identification': None, 'path': u'008002001',
                'module_path': u'008',
                'postponed': False, 'id': 324836},
                {'title': u'Le conducteur connait-il le lieu de livraison avant le d\xe9part ?',
                'priority': u'low',
                'identification': None, 'path': u'008001001',
                'module_path': u'008',
                'postponed': False, 'id': 324834},
                {'title': u'Une maintenance pr\xe9ventive est-elle effectu\xe9e sur tous les v\xe9hicules ?',
                'priority': u'low',
                'identification': None, 'path': u'007002001',
                'module_path': u'007',
                'postponed': False, 'id': 324831},
                {'title': u"Le conducteur a-t-il \xe9t\xe9 sensibilis\xe9 aux questions d'hygi\xe8ne de vie et d'addictions ? ", 'priority': u'high',
                'identification': None, 'path': u'007001004',
                'module_path': u'007',
                'postponed': False, 'id': 324829},
                {'title': u"L'utilisation du t\xe9l\xe9phone dans une phase de conduite est-elle interdite ? ", 'priority': u'low',
                'identification': None, 'path': u'007001003',
                'module_path': u'007',
                'postponed': False, 'id': 324828},
                {'title': u'Les d\xe9placements sont-ils organis\xe9s en tenant compte des d\xe9lais de livraison et des dur\xe9es de conduite de nuit ?  ',
                'priority': u'low',
                'identification': None, 'path': u'007001002',
                'module_path': u'007',
                'postponed': False, 'id': 324827},
                {'title': u'Le v\xe9hicule est-il \xe9quip\xe9 de dispositifs de s\xe9curit\xe9 et de confort ? ',
                'priority': u'low',
                'identification': None, 'path': u'007001001',
                'module_path': u'007',
                'postponed': False, 'id': 324826},
                {'title': u'Le conducteur peut-il fermer toutes les ouvertures depuis le sol ?',
                'priority': u'low',
                'identification': None, 'path': u'006001002',
                'module_path': u'006',
                'postponed': False, 'id': 324823},
                {'title': u'Le conducteur se d\xe9place-t-il sur une zone d\xe9gag\xe9e et propre ?',
                'priority': u'low',
                'identification': None, 'path': u'006001001',
                'module_path': u'006',
                'postponed': False, 'id': 324822},
                {'title': u"Le conducteur peut-il effectuer l'arrimage depuis le plancher ?", 'priority': u'low',
                'identification': None, 'path': u'005001002',
                'module_path': u'005',
                'postponed': False, 'id': 324819},
                {'title': u"Le conducteur peut-il positionner les sangles d'arrimage sans effort excessif ? ", 'priority': u'low',
                'identification': None, 'path': u'005001001',
                'module_path': u'005',
                'postponed': False, 'id': 324818},
                {'title': u"Le conducteur est-il familiaris\xe9 \xe0 la lecture des \xe9tiquettes des produits chimiques qu'il peut \xeatre amen\xe9 \xe0 transporter ?", 'priority': u'low',
                'identification': None, 'path': u'004007001',
                'module_path': u'004',
                'postponed': False, 'id': 324815},
                {'title': u"Le conducteur dispose-t-il de b\xe9quilles/tr\xe9teaux de soutien pour \xe9viter la chute d'une remorque non \xe9quip\xe9e ?", 'priority': u'low',
                'identification': None, 'path': u'004006001',
                'module_path': u'004',
                'postponed': False, 'id': 324813},
                {'title': u'Les manutentions assur\xe9es par le conducteur avec des transpalettes manuels sont-elles rares ou faiblement importantes (en nombre ou en poids) ?',
                'priority': u'low',
                'identification': None, 'path': u'004005001',
                'module_path': u'004',
                'postponed': False, 'id': 324811},
                {'title': u'Le conducteur est-il correctement form\xe9 et habilit\xe9 \xe0 la conduite de chariots \xe9l\xe9vateurs ?',
                'priority': u'low',
                'identification': u'yes',
                'path': u'004004001',
                'module_path': u'004',
                'postponed': False, 'id': 324809},
                {'title': u"Le conducteur est-il \xe0 l'abris d'une agression ?", 'priority': u'low',
                'identification': None, 'path': u'004003004',
                'module_path': u'004',
                'postponed': False, 'id': 324807},
                {'title': u'Le conducteur peut-il \xe9viter de monter sur le plateau ou sur le hayon ?',
                'priority': u'low',
                'identification': None, 'path': u'004003003',
                'module_path': u'004',
                'postponed': False, 'id': 324806},
                {'title': u"Le conducteur est-t-il prot\xe9g\xe9 des risques de coupures et de chutes d'objets ?", 'priority': u'low',
                'identification': None, 'path': u'004003002',
                'module_path': u'004',
                'postponed': False, 'id': 324805},
                {'title': u"Le conducteur utilise-t-il des \xe9quipements d'aide \xe0 la manutention ?", 'priority': u'low',
                'identification': None, 'path': u'004003001',
                'module_path': u'004',
                'postponed': False, 'id': 324804},
                {'title': u"Le conducteur dispose-t-il d'une aide automatis\xe9e pour effectuer cette man\u0153uvre ? ", 'priority': u'low',
                'identification': None, 'path': u'004002002',
                'module_path': u'004',
                'postponed': False, 'id': 324802},
                {'title': u'Le conducteur peut-il effectuer la man\u0153uvre depuis le sol ?',
                'priority': u'low',
                'identification': None, 'path': u'004002001',
                'module_path': u'004',
                'postponed': False, 'id': 324801},
                {'title': u'Le conducteur circule-t-il dans une zone propre ?',
                'priority': u'low',
                'identification': None, 'path': u'004001002',
                'module_path': u'004',
                'postponed': False, 'id': 324799},
                {'title': u'Le conducteur est-il prot\xe9g\xe9 des autres v\xe9hicules quand il \xe9volue au sol ?',
                'priority': u'high',
                'identification': u'no',
                'path': u'004001001',
                'module_path': u'004',
                'postponed': False, 'id': 324798},
                {'title': u'Le conducteur fait-il le tour de la remorque sans passer dessous ?',
                'priority': u'low',
                'identification': None, 'path': u'002003002',
                'module_path': u'002',
                'postponed': True, 'id': 324788},
                {'title': u'La mise en place des b\xe9quilles est-elle motoris\xe9e ?',
                'priority': u'low',
                'identification': None, 'path': u'002003001',
                'module_path': u'002',
                'postponed': True, 'id': 324787},
                {'title': u"Le conducteur est-il prot\xe9g\xe9 du danger d'\xe9crasement entre la remorque et la cabine ?", 'priority': u'low',
                'identification': None, 'path': u'002002001',
                'module_path': u'002',
                'postponed': True, 'id': 324785},
                {'title': u'Le conducteur circule-t-il toujours sur une zone propre ?',
                'priority': u'medium',
                'identification': u'no',
                'path': u'002001004',
                'module_path': u'002',
                'postponed': False, 'id': 324783},
                {'title': u'Le frein de parc est-il toujours actionn\xe9, d\xe8s que le conducteur quitte son v\xe9hicule ?',
                'priority': u'low',
                'identification': u'no',
                'path': u'002001003',
                'module_path': u'002',
                'postponed': False, 'id': 324782},
                {'title': u"Le conducteur est-il prot\xe9g\xe9 des autres v\xe9hicules lorsqu'il circule au sol ?", 'priority': u'medium',
                'identification': u'no',
                'path': u'002001002',
                'module_path': u'002',
                'postponed': False, 'id': 324781},
                {'title': u"Le conducteur effectue-t-il toutes ses man\u0153uvres d'accroche/d\xe9croche depuis le sol ?", 'priority': u'high',
                'identification': u'no',
                'path': u'002001001',
                'module_path': u'002',
                'postponed': False, 'id': 324780},
                {'title': u'Le conducteur circule-t-il sur une zone propre ?',
                'priority': u'low',
                'identification': u'yes',
                'path': u'001002002',
                'module_path': u'001',
                'postponed': False, 'id': 324777},
                {'title': u"Le conducteur est-il prot\xe9g\xe9 des autres v\xe9hicules lorsqu'il \xe9volue au sol ?", 'priority': u'low',
                'identification': u'yes',
                'path': u'001002001',
                'module_path': u'001',
                'postponed': False, 'id': 324776},
                {'title': u'asdg',
                'priority': u'medium',
                'identification': u'no',
                'path': u'001001003',
                'module_path': u'001',
                'postponed': False, 'id': 324774},
                {'title': u'Le conducteur circule-t-il sur une zone propre ?',
                'priority': u'low',
                'identification': u'yes',
                'path': u'001001002',
                'module_path': u'001',
                'postponed': False, 'id': 324773},
                {'title': u'Le conducteur descend-il de sa cabine en utilisant les marches ?',
                'priority': u'high',
                'identification': u'no',
                'path': u'001001001',
                'module_path': u'001',
                'postponed': False, 'id': 324772}]

        view.getModules = getModules
        view.getRisk = getRisks
        status = view.getStatus()
