from osha.oira.tests.base import OiRAFunctionalTestCase
from Testing.ZopeTestCase import FunctionalDocFileSuite

import doctest
import glob
import os.path
import unittest


def test_suite():
    location = os.path.dirname(__file__) or "."
    doctests = [
        "stories/" + os.path.basename(test)
        for test in glob.glob(os.path.join(location, "stories", "*.txt"))
    ]

    options = (
        doctest.REPORT_ONLY_FIRST_FAILURE
        | doctest.ELLIPSIS
        | doctest.NORMALIZE_WHITESPACE
    )

    suites = [
        FunctionalDocFileSuite(
            test,
            optionflags=options,
            test_class=OiRAFunctionalTestCase,
            module_relative=True,
            package="osha.oira.content.tests",
            encoding="utf-8",
        )
        for test in doctests
    ]
    return unittest.TestSuite(suites)
