from Testing.ZopeTestCase import TestCase
from osha.oira import utils

class MockActionPlan:
    def __init__(self, action_plan):
        self.action_plan = action_plan

class MockModule:
    type = 'module'
    def __init__(self, id, depth):
        self.id = id
        self.depth = depth

class MockRisk:
    type = 'risk'
    def __init__(self, id, probability, action_plans=[]):
        self.id = id
        self.probability = probability
        self.action_plans = action_plans


class TestUtils(TestCase):
    """ """

    def test_utils_methods(self):
        """ Tests the following methods in osha.oira/utils.py:
                remove_empty_modules(ls)
                get_unactioned_nodes(ls)
                get_actioned_nodes(ls)
        """
        m = MockModule 
        r = MockRisk
        ap = MockActionPlan('dummy')

        # Test a few variations of unactioned risks:
        nodes = [m('1', 1), r('1.1', 0), r('1.2', 0), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 0, )]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], ['1', '1.1', '1.2', '2', '2.1', '2.1.1', '2.1.1.1'])

        nodes = [m('1', 1), r('1.1', 0), r('1.2', 0), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 0, [ap])]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], ['1', '1.1', '1.2'])

        nodes = [m('1', 1), r('1.1', 0), r('1.2', 0), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 9, [ap])]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], ['1', '1.1', '1.2'])

        nodes = [m('1', 1), r('1.1', 3, [ap]), r('1.2', 2, [ap]), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 0, [ap])]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], [])

        nodes = [m('1', 1), r('1.1', 2, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 1), r('3', 3)]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], ['3', '3'])

        nodes = [m('1', 1), r('1.1', 0, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 1), r('3.1', 3)]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], ['3', '3.1'])

        nodes = [m('1', 1), r('1.1', 2, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 1), r('3.1', 3, [ap])]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], [])

        # Test a few variations of actioned risks:
        nodes = [m('1', 1), r('1.1', 0), r('1.2', 0), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 0, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['2', '2.1', '2.1.1', '2.1.1.1'])

        nodes = [m('1', 1), r('1.1', 0), r('1.2', 0), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 9, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['2', '2.1', '2.1.1', '2.1.1.1'])

        nodes = [m('1', 1), r('1.1', 3, [ap]), r('1.2', 2, [ap]), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 0, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['1', '1.1', '1.2', '2', '2.1', '2.1.1', '2.1.1.1'])

        nodes = [m('1', 1), r('1.1', 2, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 1), r('3.1', 3)]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['1', '1.1', '1.2'])

        nodes = [m('1', 1), r('1.1', 0, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 1), r('3.1', 3, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['1', '1.1', '1.2', '3', '3.1'])

        nodes = [m('1', 1), r('1.1', 2, [ap]), r('1.2', 3, [ap]), m('2', 1), m('2.1', 2), r('2.1.1', 3, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['1', '1.1', '1.2', '2', '2.1', '2.1.1'])

        nodes = [m('1', 1), m('1.1', 2), r('1.1.1', 3, [ap]), m('1.2', 2), m('1.2.1', 3), r('1.2.1.1', 4), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 0, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['1', '1.1', '1.1.1', '2', '2.1', '2.1.1', '2.1.1.1'])

        # Issue 3265
        nodes = [m('1', 1), m('1.1', '2'), r('1.1.1', 3), m('2', 1), m('2.1', '2'), r('2.1.1', 3, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['2', '2.1', '2.1.1'])

        nodes = [m('1', 1), m('1.1', '2'), m('1.1.1', 3), m('2', 1), m('2.1', '2'), r('2.1.1', 3, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['2', '2.1', '2.1.1'])

        nodes = [m('1', 1), m('1.1', '2'), r('1.1.1', 3, [ap]), m('2', 1), m('2.1', '2'), r('2.1.1', 3)]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['1', '1.1', '1.1.1'])

        nodes = [m('1', 1), m('1.1', '2'), r('1.1.1', 3), m('2', 1), m('2.1', '2'), r('2.1.1', 3)]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], [])


