import unittest
from unittest import makeSuite

from zope.testing import doctestunit
from zope.component import testing

from Testing.ZopeTestCase import TestCase
from osha.oira import utils

class TestUtils(TestCase):
    """Base class used for test cases
    """

    def test_utils_methods(self):
        """ Tests:
                remove_empty_modules(ls)
                get_unevaluated_nodes(ls)
                get_evaluated_nodes(ls)
        """

        class action_plan:

            def __init__(self, action_plan):
                self.action_plan = action_plan


        class module:
            type = 'module'

            def __init__(self, id, depth):
                self.id = id
                self.depth = depth

        class risk:
            type = 'risk'

            def __init__(self, id, probability, action_plans=[]):
                self.id = id
                self.probability = probability
                self.action_plans = action_plans

        m = module
        r = risk
        ap = action_plan('dummy')


        # Test a few variations of unevaluated risks:
        nodes = [m('1', 1), r('1.1', 0), r('1.2', 0), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 0, [ap])]
        unevaluated_nodes = utils.get_unevaluated_nodes(nodes)
        self.assertEquals([n.id for n in unevaluated_nodes], ['1', '1.1', '1.2', '2', '2.1', '2.1.1', '2.1.1.1'])

        nodes = [m('1', 1), r('1.1', 0), r('1.2', 0), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 9, [ap])]
        unevaluated_nodes = utils.get_unevaluated_nodes(nodes)
        self.assertEquals([n.id for n in unevaluated_nodes], ['1', '1.1', '1.2'])

        nodes = [m('1', 1), r('1.1', 3, [ap]), r('1.2', 2, [ap]), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 0, [ap])]
        unevaluated_nodes = utils.get_unevaluated_nodes(nodes)
        self.assertEquals([n.id for n in unevaluated_nodes], ['2', '2.1', '2.1.1', '2.1.1.1'])

        nodes = [m('1', 1), r('1.1', 2, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 1), r('3', 3)]
        unevaluated_nodes = utils.get_unevaluated_nodes(nodes)
        self.assertEquals([n.id for n in unevaluated_nodes], ['3', '3'])

        nodes = [m('1', 1), r('1.1', 0, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 1), r('3.1', 3)]
        unevaluated_nodes = utils.get_unevaluated_nodes(nodes)
        self.assertEquals([n.id for n in unevaluated_nodes], ['1', '1.1', '3', '3.1'])

        nodes = [m('1', 1), r('1.1', 2, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 1), r('3.1', 3, [ap])]
        unevaluated_nodes = utils.get_unevaluated_nodes(nodes)
        self.assertEquals([n.id for n in unevaluated_nodes], [])

        # Test a few variations of evaluated risks:
        nodes = [m('1', 1), r('1.1', 0), r('1.2', 0), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 0, [ap])]
        evaluated_nodes = utils.get_evaluated_nodes(nodes)
        self.assertEquals([n.id for n in evaluated_nodes], [])

        nodes = [m('1', 1), r('1.1', 0), r('1.2', 0), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 9, [ap])]
        evaluated_nodes = utils.get_evaluated_nodes(nodes)
        self.assertEquals([n.id for n in evaluated_nodes], ['2', '2.1', '2.1.1', '2.1.1.1'])

        nodes = [m('1', 1), r('1.1', 3, [ap]), r('1.2', 2, [ap]), m('2', 1), m('2.1', 2), m('2.1.1', 3), r('2.1.1.1', 0, [ap])]
        evaluated_nodes = utils.get_evaluated_nodes(nodes)
        self.assertEquals([n.id for n in evaluated_nodes], ['1', '1.1', '1.2'])

        nodes = [m('1', 1), r('1.1', 2, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 1), r('3.1', 3)]
        evaluated_nodes = utils.get_evaluated_nodes(nodes)
        self.assertEquals([n.id for n in evaluated_nodes], ['1', '1.1', '1.2'])

        nodes = [m('1', 1), r('1.1', 0, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 1), r('3.1', 3, [ap])]
        evaluated_nodes = utils.get_evaluated_nodes(nodes)
        self.assertEquals([n.id for n in evaluated_nodes], ['1', '1.2', '3', '3.1'])

        nodes = [m('1', 1), r('1.1', 2, [ap]), r('1.2', 3, [ap]), m('2', 1), m('3', 2), r('3.1', 3, [ap])]
        evaluated_nodes = utils.get_evaluated_nodes(nodes)
        self.assertEquals([n.id for n in evaluated_nodes], ['1', '1.1', '1.2', '2', '3', '3.1'])






def test_suite():
    suite = unittest.TestSuite([
        # Unit tests for your API
        doctestunit.DocFileSuite(
            'README.txt', package='osha.oira',
            setUp=testing.setUp, tearDown=testing.tearDown),

        # doctestunit.DocTestSuite(
        #     module='osha.oira.mymodule',
        #     setUp=testing.setUp, tearDown=testing.tearDown),

        # Integration tests that use ZopeTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='osha.oira',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='osha.oira'),

        ])
    suite.addTest(makeSuite(TestUtils))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
