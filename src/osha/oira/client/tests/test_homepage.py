from json import loads
from osha.oira.client.interfaces import IOSHAClientSkinLayer
from osha.oira.client import client
from osha.oira.tests.base import OiRATestCase
from plone import api
from plone.dexterity.utils import createContentInContainer
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


JSON = '''[{
"author_id":"81e55fda-86e7-4de0-87b8-f3b532fadf33",
"author_logo":"http://osha.edw.ro/sites/default/files/partners_logo/Campofrio_logo.png",
"author_name":"Campofrio",
"body":"Body text",
"body_alt":"Body alt text",
"country_code":"ES",
"country_name":"Spain",
"language_code":"es",
"language_name":"Spanish",
"revised_date":"2016-07-20 08:00:00",
"sector_name":"Driving Schools",
"title":"Driving Schools",
"title_alt":"Autoescuelas",
"tool_id":"e100dac5-6b54-47e1-9adc-64c7f2f9fae6",
"tool_link":"https://client.oiraproject.eu/es/autoescuelas/autoescuelas",
"tool_type":"OiRA",
"tool_url":"http://osha.edw.ro/en/oira-tools/driving-schools"
}]
'''


class HomepageTest(OiRATestCase):

    def setUp(self):
        super(HomepageTest, self).setUp()
        self.portal = self.layer.portal
        self.loginAsPortalOwner()
        self.request = self.portal.client.REQUEST
        alsoProvides(self.request, IOSHAClientSkinLayer)
        self.view = getMultiAdapter(
            (self.portal.client, self.request), name='view')
        self.logout()

    def raise_attr_error(self):
        raise AttributeError

    def test_initial_bad_json_url(self):
        client.get_json = self.raise_attr_error
        self.assertEquals(self.view.cached_json, [])

    def test_initial_invalid_json(self):
        client.get_json = lambda: loads('[{"auth"')
        self.assertEquals(self.view.cached_json, [])

    def test_dont_update_cached_json(self):
        client.get_json = lambda: loads('[{"a":"b"}]')
        self.view.cached_json
        client.get_json = lambda: loads('[]')
        self.assertEquals(self.view.cached_json, [{u'a': u'b'}])

    def test_update_invalid_json(self):
        client.get_json = lambda: loads('[{"auth"')
        self.view.cached_json
        client.get_json = lambda: loads('[{"a":"b"}]')
        self.assertEquals(self.view.cached_json, [{u'a': u'b'}])

    def test_manager_can_invalidate_cache(self):
        self.loginAsPortalOwner()
        client.get_json = lambda: loads('[{"a":"b"}]')
        self.view.cached_json
        self.view.request['invalidate-cache'] = 1
        client.get_json = lambda: loads('[{"a":"c"}]')
        self.assertEquals(self.view.cached_json, [{u'a': u'c'}])

    def test_anon_cannot_invalidate_cache(self):
        client.get_json = lambda: loads('[{"a":"b"}]')
        self.view.cached_json
        self.view.request['invalidate-cache'] = 1
        client.get_json = lambda: loads('[{"a":"c"}]')
        self.assertEquals(self.view.cached_json, [{u'a': u'b'}])
