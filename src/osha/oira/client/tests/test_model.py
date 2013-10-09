from euphorie.client import model
from euphorie.client.tests.database import DatabaseTests
from euphorie.client.tests.test_model import createSurvey
from osha.oira.client import utils
from z3c.saconfig import Session


class ModelQueryTests(DatabaseTests):
    """ Test #7947:

        An optional module, that's marked by the user as not
        applicable, should appear under a query for "risks determined as not
        present". Its contents should NOT appear as unanswered risks.
    """

    def createData(self):
        (self.session, self.survey) = createSurvey()
        self.mod1 = model.Module(
            title=u"Module 1", module_id="1",
            zodb_path="1", skip_children=True)
        self.survey.addChild(self.mod1)
        self.q1 = model.Risk(
            title=u"Risk 1", risk_id="1", zodb_path="1/1",
            type="risk")
        self.mod1.addChild(self.q1)

    def testUnansweredNodes(self):
        self.createData()
        self.assertEqual(len(utils.get_unanswered_nodes(self.survey)), 0)

    def testRiskNotPresentNodes(self):
        self.createData()
        self.assertEqual(len(utils.get_risk_not_present_nodes(self.survey)), 2)


class RiskQueryTests(DatabaseTests):
    """ Test #7547

        A risk with evaluation method 'fixed' (i.e. skip_evaluation=true)
        and which has been identified, should appear in the final report
        as identified but without action plan.
    """

    # TODO: We need to recreate a more accurate representation.
    #
    # Profile question containing two entries, each containing a risk.
    # Both risks are present other not. One risk has a measure.

    def createData(self):
        (self.session, self.survey) = createSurvey()

        self.q1 = model.Module(**{
            'depth': 1,
            'module_id': 1,
            'has_description': True,
            'path': u'001',
            'postponed': None,
            'profile_index': -1,
            'skip_children': False,
            'title': u'What is the sound of one hand clapping?',
            'type': u'module',
            'zodb_path': u'173'
        })
        self.survey.addChild(self.q1)

        self.mod1 = model.Module(**{
            'depth': 2,
            'module_id': 2,
            'has_description': True,
            'path': u'001001',
            'postponed': None,
            'profile_index': 0,
            'skip_children': False,
            'title': u'Stellenbosch',
            'type': u'module',
            'zodb_path': u'173'
        })
        self.q1.addChild(self.mod1)

        self.r1 = model.Risk(**{
            'risk_id': 1,
            'depth': 3,
            'identification': 'no',
            'action_plans': [],
            'has_description': True,
            'path': u'001001001',
            'postponed': False,
            'profile_index': 0,
            'skip_children': False,
            'title': u'Hands are washed',
            'type': u'risk',
            'zodb_path': u'173/euphorie.risk'
        })
        self.mod1.addChild(self.r1)

        self.mod2 = model.Module(**{
            'depth': 2,
            'module_id': 3,
            'has_description': True,
            'path': u'001002',
            'postponed': None,
            'profile_index': 1,
            'skip_children': False,
            'title': u'Somerset West',
            'type': u'module',
            'zodb_path': u'173'
        })
        self.q1.addChild(self.mod2)

        self.r2 = model.Risk(**{
            'risk_id': 1,
            'depth': 3,
            'identification': 'yes',
            'action_plans': [],
            'has_description': True,
            'path': u'001002001',
            'postponed': False,
            'profile_index': 1,
            'skip_children': False,
            'title': u'Hands are washed',
            'type': u'risk',
            'zodb_path': u'173/euphorie.risk'
        })
        self.mod2.addChild(self.r2)

        # self.r3 = model.Risk(**{
        #     'risk_id': 2,
        #     'depth': 3,
        #     'identification': 'no',
        #     'action_plans': [
        #         model.ActionPlan(action_plan='Add soap')
        #     ],
        #     'has_description': True,
        #     'path': u'001002001',
        #     'postponed': False,
        #     'profile_index': 1,
        #     'skip_children': False,
        #     'title': u'Hands are washed',
        #     'type': u'risk',
        #     'zodb_path': u'173/euphorie.risk'
        # })
        # self.mod2.addChild(self.r3)

    def testUnactionedNodes(self):
        self.createData()
        query = Session().query(model.SurveyTreeItem)\
            .filter(model.SurveyTreeItem.session == self.survey)\
            .order_by(model.SurveyTreeItem.path)

        nodes = query.all()
        import pdb; pdb.set_trace()
        self.assertEqual(len(utils.get_unactioned_nodes(nodes)), 3)

    # def testActionedNodes(self):
    #     self.createData()
    #     query = Session().query(model.SurveyTreeItem)\
    #         .filter(model.SurveyTreeItem.session == self.survey)\
    #         .order_by(model.SurveyTreeItem.path)

    #     nodes = query.all()
    #     # TODO: double check, previously expected 3 got 2
    #     self.assertEqual(len(utils.get_actioned_nodes(nodes)), 0)

    # def testUnansweredNodes(self):
    #     self.createData()
    #     self.assertEqual(len(utils.get_unanswered_nodes(self.survey)), 0)

    # def testRiskNotPresentNodes(self):
    #     self.createData()
    #     self.assertEqual(len(utils.get_risk_not_present_nodes(self.survey)), 0)
