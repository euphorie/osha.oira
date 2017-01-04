import unittest
import os
import robotsuite
from osha.oira.testing import OIRA_SUITE_ROBOT
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    for testfile in os.listdir(
            os.path.join(os.path.dirname(__file__), "acceptance")):
        testfilepath = os.path.join("acceptance", testfile)
        if os.path.isdir(testfilepath):
            continue

        if testfile.endswith('.robot'):
            suite.addTests([
                layered(
                    robotsuite.RobotTestSuite(
                        testfilepath,
                        noncritical=['fixme', 'noncritical', 'heisenbug']),
                    layer=OIRA_SUITE_ROBOT),
            ])
    return suite
