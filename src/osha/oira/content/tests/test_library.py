import mock
from osha.oira.tests.base import OiRAFunctionalTestCase
from euphorie.content.tests.utils import createSector
from euphorie.content.tests.utils import BASIC_SURVEY
from euphorie.content.tests.utils import addSurvey


class LibraryTests(OiRAFunctionalTestCase):
    library = [{'title': u'Library Sector Title',
                'url': 'http://localhost/sector',
                'surveys': [
                    {'title': u'Library Survey Title',
                     'path': '/portal/sector/survey/version',
                     'url': 'http://localhost/portal/sector/survey/version',
                     'portal_type': 'euphorie.sector',
                     'children': [
                         {'title': u'Library Risk',
                          'number': '1',
                          'path': '/portal/sector/surveys/version/1',
                          'url': 'http://localhost/portal/sector/surveys/version/1',
                          'disabled': False,
                          'portal_type': 'euphorie.risk',
                          'children': []}]}]}]

    def test_render(self):
        self.loginAsPortalOwner()
        sector = createSector(self.portal)
        survey = addSurvey(sector, BASIC_SURVEY)
        browser = self.adminBrowser()
        browser.handleErrors = False
        with mock.patch('osha.oira.content.library.get_library',
                return_value=self.library):
            browser.open(survey.absolute_url() + '/@@library')
        assert 'Library Sector Title' in browser.contents
        assert 'Library Survey Title' in browser.contents
        assert 'Library Risk' in browser.contents
