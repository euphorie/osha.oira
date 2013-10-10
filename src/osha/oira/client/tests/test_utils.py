from Testing.ZopeTestCase import TestCase
from osha.oira.client import utils


class MockActionPlan:
    def __init__(self, action_plan):
        self.action_plan = action_plan


class MockModule:
    type = 'module'

    def __init__(self, id, path, depth):
        self.id = id
        self.path = path
        self.depth = depth


class MockRisk:
    type = 'risk'

    def __init__(self, id, path, probability, action_plans=[]):
        self.id = id
        self.path = path
        self.probability = probability
        self.action_plans = action_plans


class TestUtils(TestCase):
    """ """

    def test_remove_empty_modules(self):
        m = MockModule
        r = MockRisk
        nodes = [
            m('1', '001', 1),
            r('1.1', '001001', 2),
            r('1.2', '001002', 2),
            m('2', '002', 1),  # Should be removed, no subrisks
            m('3', '003', 1),
            m('3.1', '003001', 2),
            r('3.1.1', '003001001', 3),
            m('4', '004', 1),  # Should stay, has 4.2.2
            m('4.1', '004001', 2),  # Should be removed, no subrisks
            m('4.2', '004002', 2),
            r('4.2.2', '004002002', 3)
        ]
        new_nodes = utils.remove_empty_modules(nodes)
        self.assertEquals(
            [n.id for n in new_nodes],
            [
                '1',
                '1.1',
                '1.2',
                '3',
                '3.1',
                '3.1.1',
                '4',
                '4.2',
                '4.2.2',
            ]
        )

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
        nodes = [m('1', '001', 1),
                 r('1.1', '001001', 0),
                 r('1.2', '001002', 0),
                 m('2', '002', 1),
                 m('2.1', '002001', 2),
                 m('2.1.1', '002001001', 3),
                 r('2.1.1.1', '002001001001', 0, )]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in unactioned_nodes],
            ['1', '1.1', '1.2', '2', '2.1', '2.1.1', '2.1.1.1']
        )

        nodes = [m('1', '001', 1),
                 r('1.1', '001001', 0),
                 r('1.2', '001002', 0),
                 m('2', '002', 1),
                 m('2.1', '002001', 2),
                 m('2.1.1', '002001001', 3),
                 r('2.1.1.1', '002001001001', 0, [ap])]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in unactioned_nodes],
            ['1', '1.1', '1.2']
        )

        nodes = [m('1', '001', 1),
                 r('1.1', '001001', 0),
                 r('1.2', '001002', 0),
                 m('2', '002', 1),
                 m('2.1', '002001', 2),
                 m('2.1.1', '002001001', 3),
                 r('2.1.1.1', '002001001001', 9, [ap])]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in unactioned_nodes],
            ['1', '1.1', '1.2']
        )

        nodes = [m('1', '001', 1),
                 r('1.1', '001001', 3, [ap]),
                 r('1.2', '001002', 2, [ap]),
                 m('2', '002', 1),
                 m('2.1', '002001', 2),
                 m('2.1.1', '002001001', 3),
                 r('2.1.1.1', '002001001001', 0, [ap])]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], [])

        nodes = [m('1', '001', 1),
                 r('1.1', '001001', 2, [ap]),
                 r('1.2', '001002', 3, [ap]),
                 m('2', '002', 1),
                 m('3', '003', 1),
                 r('3', '003', 3)]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], ['3', '3'])

        nodes = [m('1', '001', 1),
                 r('1.1', '001001', 0, [ap]),
                 r('1.2', '001002', 3, [ap]),
                 m('2', '002', 1),
                 m('3', '003', 1),
                 r('3.1', '003001', 3)]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], ['3', '3.1'])

        nodes = [m('1', '001', 1),
                 r('1.1', '001001', 2, [ap]),
                 r('1.2', '001002', 3, [ap]),
                 m('2', '002', 1),
                 m('3', '003', 1),
                 r('3.1', '003001', 3, [ap])]
        unactioned_nodes = utils.get_unactioned_nodes(nodes)
        self.assertEquals([n.id for n in unactioned_nodes], [])

        # Test a few variations of actioned risks:
        nodes = [m('1', '001', 1),
                 r('1.1', '001001', 0),
                 r('1.2', '001002', 0),
                 m('2', '002', 1),
                 m('2.1', '002001', 2),
                 m('2.1.1', '002001001', 3),
                 r('2.1.1.1', '002001001001', 0, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in actioned_nodes],
            ['2', '2.1', '2.1.1', '2.1.1.1']
        )

        nodes = [m('1', '001', 1),
                 r('1.1', '001001', 0),
                 r('1.2', '001002', 0),
                 m('2', '002', 1),
                 m('2.1', '002001', 2),
                 m('2.1.1', '002001001', 3),
                 r('2.1.1.1', '002001001001', 9, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in actioned_nodes],
            ['2', '2.1', '2.1.1', '2.1.1.1']
        )

        nodes = [
            m('1', '001', 1),
            r('1.1', '001001', 3, [ap]),
            r('1.2', '001002', 2, [ap]),
            m('2', '002', 1),
            m('2.1', '002001', 2),
            m('2.1.1', '002001001', 3),
            r('2.1.1.1', '002001001001', 0, [ap])
        ]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in actioned_nodes],
            ['1', '1.1', '1.2', '2', '2.1', '2.1.1', '2.1.1.1']
        )

        nodes = [m('1', '001', 1),
                 r('1.1', '001001', 2, [ap]),
                 r('1.2', '001002', 3, [ap]),
                 m('2', '002', 1),
                 m('3', '003', 1),
                 r('3.1', '003001', 3)]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], ['1', '1.1', '1.2'])

        nodes = [
            m('1', '001', 1),
            r('1.1', '001001', 0, [ap]),
            r('1.2', '001002', 3, [ap]),
            m('2', '002', 1),
            m('3', '003', 1),
            r('3.1', '003001', 3, [ap])
        ]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in actioned_nodes],
            ['1', '1.1', '1.2', '3', '3.1']
        )

        nodes = [
            m('1', '001', 1),
            r('1.1', '001001', 2, [ap]),
            r('1.2', '001002', 3, [ap]),
            m('2', '002', 1),
            m('2.1', '002001', 2),
            r('2.1.1', '002001001', 3, [ap])
        ]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in actioned_nodes],
            ['1', '1.1', '1.2', '2', '2.1', '2.1.1']
        )

        nodes = [m('1', '001', 1),
                 m('1.1', '001001', 2),
                 r('1.1.1', '001001001', 3, [ap]),
                 m('1.2', '001002', 2),
                 m('1.2.1', '001002001', 3),
                 r('1.2.1.1', '001002001001', 4),
                 m('2', '002', 1),
                 m('2.1', '002001', 2),
                 m('2.1.1', '002001001', 3),
                 r('2.1.1.1', '002001001001', 0, [ap])]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in actioned_nodes],
            ['1', '1.1', '1.1.1', '2', '2.1', '2.1.1', '2.1.1.1']
        )

        # Issue 3265
        nodes = [
            m('1', '001', 1),
            m('1.1', '001001', '002'),
            r('1.1.1', '001001001', 3),
            m('2', '002', 1),
            m('2.1', '002001', '002'),
            r('2.1.1', '002001001', 3, [ap])
        ]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in actioned_nodes],
            ['2', '2.1', '2.1.1']
        )

        nodes = [
            m('1', '001', 1),
            m('1.1', '001001', '002'),
            m('1.1.1', '001001001', 3),
            m('2', '002', 1),
            m('2.1', '002001', '002'),
            r('2.1.1', '002001001', 3, [ap])
        ]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in actioned_nodes],
            ['2', '2.1', '2.1.1']
        )

        nodes = [
            m('1', '001', 1),
            m('1.1', '001001', '002'),
            r('1.1.1', '001001001', 3, [ap]),
            m('2', '002', 1),
            m('2.1', '002001', '002'),
            r('2.1.1', '002001001', 3)
        ]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals(
            [n.id for n in actioned_nodes],
            ['1', '1.1', '1.1.1']
        )

        nodes = [
            m('1', '001', 1),
            m('1.1', '001001', '002'),
            r('1.1.1', '001001001', 3),
            m('2', '002', 1),
            m('2.1', '002001', '002'),
            r('2.1.1', '002001001', 3)
        ]
        actioned_nodes = utils.get_actioned_nodes(nodes)
        self.assertEquals([n.id for n in actioned_nodes], [])
