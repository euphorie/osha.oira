from osha.oira.testing import OIRA_FUNCTIONAL_TESTING
from plone.testing import layered

import doctest
import glob
import logging
import os.path
import unittest


logger = logging.getLogger("osha.oira.tests.test_doctests")


def test_suite():
    suite = unittest.TestSuite()

    logger.info("SKIP TEST: Doctests need fixing.")
    return suite

    location = os.path.dirname(__file__) or "."
    doc_tests = [
        "stories/" + os.path.basename(test)
        for test in glob.glob(os.path.join(location, "stories", "*.txt"))
    ]

    option_flags = (
        doctest.REPORT_ONLY_FIRST_FAILURE
        | doctest.ELLIPSIS
        | doctest.NORMALIZE_WHITESPACE
    )

    suite.addTests(
        [
            layered(
                doctest.DocFileSuite(test_file, optionflags=option_flags),
                layer=OIRA_FUNCTIONAL_TESTING,
            )
            for test_file in doc_tests
        ]
    )
    return suite
