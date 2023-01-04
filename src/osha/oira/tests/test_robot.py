from osha.oira.testing import OIRA_SUITE_ROBOT
from plone.testing import layered

import logging
import os
import robotsuite
import unittest


logger = logging.getLogger("osha.oira.tests.test_robot")


def test_suite():
    suite = unittest.TestSuite()

    logger.info("SKIP TEST: Robot tests need fixing.")
    return suite

    for testfile in os.listdir(os.path.join(os.path.dirname(__file__), "acceptance")):
        testfilepath = os.path.join("acceptance", testfile)
        if os.path.isdir(testfilepath):
            continue

        if testfile.endswith(".robot"):
            suite.addTests(
                [
                    layered(
                        robotsuite.RobotTestSuite(
                            testfilepath,
                            noncritical=["fixme", "noncritical", "heisenbug"],
                        ),
                        layer=OIRA_SUITE_ROBOT,
                    ),
                ]
            )
    return suite
