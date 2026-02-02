from osha.oira.ploneintranet.quaive_links import SurveyLinks
from osha.oira.testing import OIRA_INTEGRATION_TESTING
from plone import api

import unittest


class TestOiraLinksStatusView(unittest.TestCase):
    layer = OIRA_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_url_extraction_with_unicode(self):
        testurl_1 = "https://ok.net/%20including%20encoded%20whitespace/@@view"
        testurl_2 = "https://pypi.org/project/urlextract/"
        # Only matches https://test.com/, as unquoted whitespace isn't supported.
        testurl_3 = "https://test.com/ including some whitespace/@@view"
        # A real example from the island
        testurl_4 = "https://ust.is/library/Skrar/Atvinnulif/Efni/Eftirlit/UST20206-063_-_Eftirlitsskýrsla-_Fálkinn_Ísmar.pdf"  # noqa: E501
        # One with load of umlauts.
        testurl_5 = "https://ååå.éëþüú.is/óö«/áßð.æíï"

        text = """
        それも将来始めてこの干渉人に対してのの頃に罹りないん。ほとんど多年を創設
        方もしばしばその意味なですだけをするてっんには反抗もつましでて、ちょっと
        にも考えますなくますた。事をしないはずはどうしても場合にむしろですでしょ
        """

        # Set up text including multiple test urls.
        # Mix the order of the URLs to also test the stable ordering.
        description: str = (
            text
            + testurl_2
            + text
            + testurl_1
            + text
            + testurl_5
            + ".,;:!?"  # should not include punctuation characters.
            + text
            + testurl_4
            + "'"  # should not include quotes
            + '"'
            + testurl_3
            + "<>[]{}()"  # Also no parentheses
        )

        with api.env.adopt_user("admin"):
            # Let's just test on a simple document instead of a full survey to
            # avoid setting up all the boiler plate.
            document = api.content.create(
                self.portal,
                type="Document",
                id="test",
                title="Test",
                description=description,
            )

        view = SurveyLinks(document, self.request.clone())
        result: list = list(view.extract_links(document))
        self.assertEqual(result[0]["url"], "http://nohost/plone/test")
        self.assertEqual(result[0]["title"], "Test")
        self.assertEqual(len(result[0]["links"]), 5)

        # Stable sorting, therefore not in the same order as in the document.
        self.assertEqual(result[0]["links"][0]["url"], testurl_1)
        self.assertEqual(result[0]["links"][1]["url"], testurl_2)
        # No support for unencoded whitespace in URLs.
        self.assertEqual(result[0]["links"][2]["url"], "https://test.com/")
        self.assertEqual(result[0]["links"][3]["url"], testurl_4)
        self.assertEqual(result[0]["links"][4]["url"], testurl_5)

    def test_url_extraction_with_escaped_characters(self):
        testurl = "https://pypi.org/project/osha.oira/?a=1&amp;b=2&amp;c=3"
        testurl_unescaped = "https://pypi.org/project/osha.oira/?a=1&b=2&c=3"

        text = "それも将来始めてこの干渉人"

        description: str = text + " " + testurl + " " + text

        with api.env.adopt_user("admin"):
            # Let's just test on a simple document instead of a full survey to
            # avoid setting up all the boiler plate.
            document = api.content.create(
                self.portal,
                type="Document",
                id="test",
                title="Test",
                description=description,
            )

        view = SurveyLinks(document, self.request.clone())
        result: list = list(view.extract_links(document))
        self.assertEqual(len(result[0]["links"]), 1)
        self.assertEqual(result[0]["links"][0]["url"], testurl_unescaped)
