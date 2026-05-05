from lxml import etree
from osha.oira.content.browser.map_images import MapImages
from unittest import mock
from unittest import TestCase


class DummySurvey:
    def __init__(self, survey_id, image=None):
        self._id = survey_id
        self.image = image

    def getId(self):
        return self._id


class DummySurveyGroup(dict):
    def __init__(self, surveys, published=None):
        super().__init__((survey.getId(), survey) for survey in surveys)
        self.published = published


class TestMapImages(TestCase):

    def make_view(self):
        """Helper to create a MapImages view with a temporary images path."""
        return MapImages(context=mock.sentinel.context, request=mock.Mock())

    def test_get_filename(self):
        view = self.make_view()
        elem = etree.HTML(
            '<img src="/sites/oira_revamp/.../generic%20item_A%20-%20300.jpg?itok=EYPWQiLw" />'  # noqa: E501
        )
        img = elem.find(".//img")

        self.assertEqual(view.get_filename(img), "generic item_A - 300.png")

    def test_get_tool_path(self):
        view = self.make_view()
        elem = etree.HTML(
            "<div>"
            '  <div class="button-risk">'
            '    <a href="/en/tools/eu/eu-horeca/oira-horeca?foo=bar"></a>'
            "  </div>"
            "</div>"
        )

        self.assertEqual(view.get_tool_path(elem), "eu/eu-horeca/oira-horeca")
